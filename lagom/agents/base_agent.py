class BaseAgent(object):
    """
    Base class of the agent for action selection and learning rule. 
    
    Depending on the type of agent (e.g. policy-based or value-based), it is recommended
    to override the constructor __init__() to provide essential items for the agent. 
    
    All inherited subclasses should implement the following functions:
    1. choose_action(self, obs)
    2. learn(self, x)
    3. save(self, filename)
    4. load(self, filename)
    """
    def __init__(self, config):
        """
        Args:
            config (dict): the configurations
        """
        self.config = config
        
    def choose_action(self, obs):
        """
        The agent selects an action based on given observation. 
        The output is a dictionary containing useful items, e.g. action, action_logprob, state_value
        
        Args:
            obs (object): agent's observation
            
        Returns:
            output (dict): a dictionary of action selection output. 
                Possible keys: ['action', 'action_logprob', 'state_value', 'Q_value']
        """
        raise NotImplementedError
        
    def learn(self, x):
        """
        Learning rule about how agent updates itself given data.
        The output is a dictionary containing useful items, i.e. total_loss, batched_policy_loss
        
        Args:
            x (object): input data to train the agent. 
                e.g. In policy gradient, this can be a list of episodes
            
        Returns:
            output (dict): a dictionary of learning output. 
                Possible keys: ['total_loss', 'batched_policy_loss']
        """
        raise NotImplementedError
        
    def save(self, filename):
        """
        Save the current parameters of the agent. 
        
        If the agent uses a BaseNetwork object, it is recommended to call
        BaseNetwork internal save/load function for network parameters in PyTorch. 
        
        Args:
            filename (str): name of the file
        """
        raise NotImplementedError
        
    def load(self, filename):
        """
        Load the parameters of the agent from a file
        
        If the agent uses a BaseNetwork object, it is recommended to call
        BaseNetwork internal save/load function for network parameters in PyTorch. 
        
        Args:
            filename (str): name of the file
        
        """
        raise NotImplementedError