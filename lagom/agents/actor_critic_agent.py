import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F

from .base_agent import BaseAgent
from lagom.core.transform import Standardize


class ActorCriticAgent(BaseAgent):
    """
    Actor-Critic with value network (baseline), no bootstrapping to estimate value function. 
    
    Sometimes it is also called Vanilla Policy Gradient (VPG)
    """
    def __init__(self, policy, optimizer, config, **kwargs):
        self.policy = policy
        self.optimizer = optimizer
        
        super().__init__(config, **kwargs)
        
    def choose_action(self, obs):
        # Convert to Tensor
        # Note that the observation should be batched already (even if only one trajectory)
        if not torch.is_tensor(obs):
            obs = torch.from_numpy(np.array(obs)).float()
            obs = obs.to(self.device)  # move to device
            
        # Call policy
        # Note that all metrics should also be batched for TrajectoryRunner to work properly, check policy/network output.   
        out_policy = self.policy(obs)
                
        # Dictionary of output data
        output = {}
        output = {**out_policy}
                
        return output
        
    def learn(self, D):
        batch_policy_loss = []
        batch_value_loss = []
        batch_entropy_loss = []
        batch_total_loss = []
        
        # Iterate over list of trajectories in D
        for trajectory in D:
            # Get all discounted returns as estimate of Q
            Qs = trajectory.all_discounted_returns
            # TODO: when use GAE of TDs, really standardize it ? biased magnitude of learned value get wrong TD error
            # Standardize advantage estimates if required
            # encourage/discourage half of performed actions, respectively.
            if self.config['agent:standardize']:
                Qs = Standardize()(Qs)
                
            # Get all state values (without V_s_next in final transition)
            Vs = trajectory.all_info('V_s')
            
            # Advantage estimates
            As = [Q - V.item() for Q, V in zip(Qs, Vs)]
            
            # Get all log-probabilities and entropies
            logprobs = trajectory.all_info('action_logprob')
            entropies = trajectory.all_info('entropy')
            
            # Estimate policy gradient for all time steps and record all losses
            policy_loss = []
            value_loss = []
            entropy_loss = []
            for logprob, entropy, A, Q, V in zip(logprobs, entropies, As, Qs, Vs):
                policy_loss.append(-logprob*A)
                value_loss.append(F.mse_loss(V, torch.tensor(Q).view_as(V).to(V.device)))
                entropy_loss.append(-entropy)
                
            # Average over losses for all time steps
            policy_loss = torch.stack(policy_loss).mean()
            value_loss = torch.stack(value_loss).mean()
            entropy_loss = torch.stack(entropy_loss).mean()
        
            # Calculate total loss
            value_coef = self.config['agent:value_coef']
            entropy_coef = self.config['agent:entropy_coef']
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
        if self.config['agent:max_grad_norm'] is not None:
            nn.utils.clip_grad_norm_(parameters=self.policy.network.parameters(), 
                                     max_norm=self.config['agent:max_grad_norm'], 
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
    
    def save(self, filename):
        self.policy.network.save(filename)
    
    def load(self, filename):
        self.policy.network.load(filename)
