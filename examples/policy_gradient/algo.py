import numpy as np

import torch
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F

from lagom import set_global_seeds
from lagom import BaseAlgorithm
from lagom.envs import EnvSpec
from lagom.core.utils import Logger

from lagom.envs import make_envs
from lagom.envs import make_gym_env
from lagom.envs.vec_env import SerialVecEnv

from lagom.runner import SegmentRunner

from lagom.agents import REINFORCEAgent
from lagom.agents import ActorCriticAgent
from lagom.agents import A2CAgent

from engine import Engine
from policy import MLP
from policy import CategoricalPolicy


class Algorithm(BaseAlgorithm):
    def __call__(self, config):
        # Set random seeds: PyTorch, numpy.random, random
        set_global_seeds(seed=config['seed'])
        
        # Make a list of make_env functions
        list_make_env = make_envs(make_env=make_gym_env, 
                                  env_id='CartPole-v1', 
                                  num_env=config['N'], 
                                  init_seed=config['seed']+1)
        # Create vectorized environment
        env = SerialVecEnv(list_make_env=list_make_env)
        
        # Create environment specification
        env_spec = EnvSpec(env)
        
        # Create device
        device = torch.device('cuda' if config['cuda'] else 'cpu')
        
        # Create logger
        logger = Logger(name='logger')
        
        # Create policy
        network = MLP(config=config).to(device)
        policy = CategoricalPolicy(network=network, env_spec=env_spec)

        # Create optimizer
        optimizer = optim.Adam(policy.network.parameters(), lr=config['lr'])
        # Learning rate scheduler
        max_epoch = config['train_iter']  # Max number of lr decay, Note where lr_scheduler put
        lambda_f = lambda epoch: 1 - epoch/max_epoch  # decay learning rate for each training epoch
        lr_scheduler = optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=lambda_f)
        
        # Create agent
        all_agents = [REINFORCEAgent, ActorCriticAgent, A2CAgent]
        agent_class = all_agents[2]
        agent = agent_class(policy=policy, 
                            optimizer=optimizer, 
                            config=config, 
                            lr_scheduler=lr_scheduler, 
                            device=device)
        
        # Create runner
        runner = SegmentRunner(agent=agent, 
                               env=env, 
                               gamma=config['gamma'])
        
        # Create engine
        engine = Engine(agent=agent, 
                        runner=runner, 
                        config=config, 
                        logger=logger)
        
        # Training
        train_output = engine.train()
        np.save(f'logs/returns_{agent.__class__.__name__}_{config["ID"]}', train_output)
        
        return None
