import torch
import torch.nn as nn
import torch.nn.functional as F

from .base_agent import BaseAgent
from lagom.core.transform import Standardize


class ActorCriticAgent(BaseAgent):
    """
    Actor-Critic with value network (baseline), no bootstrapping to estimate value function. 
    """
    def __init__(self, policy, optimizer, config, **kwargs):
        self.policy = policy
        self.optimizer = optimizer
        
        super().__init__(config, **kwargs)
        
    def choose_action(self, obs):
        # Convert to Tensor
        # Note that we assume obs is a single observation, not batched one
        # so we unsqueeze it with a batch dimension
        if not torch.is_tensor(obs):
            obs = torch.from_numpy(obs).float()
            obs = obs.unsqueeze(0)  # make a batch dimension
            obs = obs.to(self.device)  # move to device
        
        out_policy = self.policy(obs)
        # Squeeze the single batch dimension of the action
        for key, val in out_policy.items():
            if torch.is_tensor(val):
                out_policy[key] = val.squeeze(0)
                
        # Dictionary of output data
        output = {}
        output = {**out_policy}
                
        return output
        
    def learn(self, x):
        batch_policy_loss = []
        batch_value_loss = []
        batch_entropy_loss = []
        batch_total_loss = []
        
        # Iterate over list of trajectories
        for trajectory in x:
            # Get all discounted returns
            Rs = trajectory.all_discounted_returns
            if self.config['standardize_pg']:  # encourage/discourage half of performed actions, i.e. [-1, 1]
                Rs = Standardize()(Rs)
                
            # Get all state values (except for s_next in last transition)
            Vs = trajectory.all_V[:-1]
            
            # Get all log-probabilities and entropies
            logprobs = trajectory.all_info('action_logprob')
            entropies = trajectory.all_info('entropy')
            
            # All losses
            policy_loss = []
            value_loss = []
            entropy_loss = []
            
            # Estimate policy gradient for all time steps
            for logprob, entropy, R, V in zip(logprobs, entropies, Rs, Vs):
                # Advantage estimate
                A = R - V.item()
                # Compute losses
                policy_loss.append(-logprob*float(A))  # TODO: supports VecEnv
                value_loss.append(F.mse_loss(V, torch.tensor(float(R), device=V.device).type_as(V)))
                entropy_loss.append(-entropy)
                
            # Sum up losses for all time steps
            policy_loss = torch.stack(policy_loss).sum()
            value_loss = torch.stack(value_loss).sum()
            entropy_loss = torch.stack(entropy_loss).sum()
        
            # Calculate total loss
            value_coef = self.config['value_coef']
            entropy_coef = self.config['entropy_coef']
            total_loss = policy_loss + value_coef*value_loss + entropy_coef*entropy_loss
            
            # Record all losses
            batch_policy_loss.append(policy_loss)
            batch_value_loss.append(value_loss)
            batch_entropy_loss.append(entropy_loss)
            batch_total_loss.append(total_loss)
        
        # Compute loss (average over trajectories)
        loss = torch.stack(batch_total_loss).mean()  # use stack because each element is zero-dim tensor
        
        # Zero-out gradient buffer
        self.optimizer.zero_grad()
        # Backward pass and compute gradients
        loss.backward()
        
        # Clip gradient norms if required
        if self.config['max_grad_norm'] is not None:
            nn.utils.clip_grad_norm_(parameters=self.policy.network.parameters(), 
                                     max_norm=self.config['max_grad_norm'], 
                                     norm_type=2)
        
        # Decay learning rate if required
        if hasattr(self, 'lr_scheduler'):
            self.lr_scheduler.step()
        
        # Take a gradient step
        self.optimizer.step()
        
        # Output dictionary for different losses
        # TODO: if no more backprop needed, record with .item(), save memory without store computation graph
        output = {}
        output['loss'] = loss  # TODO: maybe item()
        output['batch_policy_loss'] = batch_policy_loss
        output['batch_value_loss'] = batch_value_loss
        output['batch_entropy_loss'] = batch_entropy_loss
        output['batch_total_loss'] = batch_total_loss
        if hasattr(self, 'lr_scheduler'):
            output['current_lr'] = self.lr_scheduler.get_lr()
        
        return output
