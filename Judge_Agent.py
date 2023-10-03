from utils.Agent import Agent


class Judge_Agent(Agent):
    def __init__(self, model_name: str, name: str, temperature: float, openai_api_key: str, sleep_time: float=0) -> None:
        """Create a player in the debate

        Args:
            model_name(str): model name
            name (str): name of this player
            temperature (float): higher values make the output more random, while lower values make it more focused and deterministic
            openai_api_key (str): As the parameter name suggests
            sleep_time (float): sleep because of rate limits
        """
        super(Judge_Agent, self).__init__(model_name, name, temperature, sleep_time)
        self.openai_api_key = openai_api_key

    # def save_json_file():

    # def send_message():

    # def broadcast():
    
