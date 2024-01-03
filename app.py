import base64
import io
import json
import os
import os.path
import re
from abc import ABC
from typing import Any
from uuid import uuid4

import gradio as gr
import requests
from PIL import Image
from langchain.chains import ConversationChain
from langchain.chat_models import AzureChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool

SAVE_FOLDER = "./img"
SDXL_API_KEY = ""
SDXL_API_SECRET = ""
AZURE_END_POINT = "https://aimodelgpt.openai.azure.com"
AZURE_OPEN_KEY = ""


class SdxlImage(BaseTool, ABC):
    name = "AI SDXL Image Generator"

    description = 'use this tool when you need to generate images by using SDXL model, To use the tool, you must ' \
                  'provide prompt parameters prompt, prompt is the description and number of the image, for example, ' \
                  'if you want to generate two images about a cute cat, set prompt = a cute cat[SEP]2'

    NEGATIVE_PROMPT = "worst quality, low quality, normal quality, lowres, watermark, monochrome, grayscale, ugly, " \
                      "blurry, Tan skin, dark skin, black skin, skin spots, skin blemishes, age spot, glans, " \
                      "disabled, distorted, bad anatomy, morbid, malformation, amputation, bad proportions, twins, " \
                      "missing body, fused body, extra head, poorly drawn face, bad eyes, deformed eye, unclear eyes, " \
                      "cross-eyed, long neck, malformed limbs, extra limbs, extra arms, missing arms, bad tongue, " \
                      "strange fingers, mutated hands, missing hands, poorly drawn hands, extra hands, fused hands, " \
                      "connected hand, bad hands, wrong fingers, missing fingers, extra fingers, 4 fingers, " \
                      "3 fingers, deformed hands, extra legs, bad legs, many legs, more than two legs, bad feet, " \
                      "wrong feet, extra feets,"

    api_key: str
    api_secret: str

    # def __init__(self, api_key, api_secret):
    #     self.api_key = api_key
    #     self.api_secret = api_secret

    def _run(
            self,
            prompt,
            **kwargs: Any,
    ) -> Any:
        print(f"execute SDXL Image Tool {prompt}")
        split_items = prompt.split("[SEP]")
        number = 1
        if len(split_items) > 1:
            prompt, number = split_items[:2]
        return self.generate_image(query=prompt, number=int(number))

    def get_access_token(self):
        """
        使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
        """
        url = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.api_secret}'

        payload = json.dumps("")
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json().get("access_token")

    def save_image(self, base64_string):
        file_path = _id = str(uuid4()) + ".png"
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        if not os.path.exists(SAVE_FOLDER):
            os.mkdir(SAVE_FOLDER)
        image.save(os.path.join(SAVE_FOLDER, file_path))
        return file_path

    def generate_image(self, query: str, number: int = 1):
        token = self.get_access_token()
        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/text2image/sd_xl?access_token=" + token

        payload = json.dumps({
            "prompt": query,
            "negative_prompt": self.NEGATIVE_PROMPT,
            "size": "768x1024",
            "steps": 25,
            "n": number,
            "sampler_index": "DPM++ SDE Karras"
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        try:
            if response and response.text:
                data = json.loads(response.text)['data']
                if data:
                    filenames = ",".join([self.save_image(sub_data['b64_image']) for sub_data in data])
                    return f"generate total {number} of the {query}, output is all the files {filenames}"
        except Exception as err:
            print(err)

        return "failed to call tool, got error message"


class AgentBot:
    def __init__(self):
        chat_llm = AzureChatOpenAI(
            azure_endpoint=AZURE_END_POINT,
            openai_api_key=AZURE_OPEN_KEY,
            deployment_name="gpt-35-turbo",
            openai_api_version="2023-10-01-preview",
            temperature=0.0
        )
        template = """你是中文情感聊天机器人，你掌握很多心理咨询和情感相关书籍，能帮助解决心理问题并提供心理辅导\
        以上是客户的历史聊天信息： {history}
        请根据客户的问题回答: {input} """

        prompt_template = PromptTemplate(
            template=template,
            input_variables=['history', 'input']
        )

        # initialize conversational memory
        conversational_memory = ConversationBufferWindowMemory(
            llm=chat_llm,
            # memory_key='history',
            k=5,
            return_messages=True
        )

        # PromptTemplate(input_variables=["history", "input"], template=DEFAULT_TEMPLATE)

        # tools = [SdxlImage(api_key=SDXL_API_KEY, api_secret=SDXL_API_SECRET)]

        # initialize agent with tools
        # self.agent = initialize_agent(
        #     agent='chat-conversational-react-description',
        #     tools=[],
        #     llm=chat_llm,
        #     verbose=True,
        #     max_iterations=3,
        #     early_stopping_method='generate',
        #     memory=conversational_memory
        # )
        self.agent = ConversationChain(llm=chat_llm,
                                       prompt=prompt_template,
                                       memory=conversational_memory)

    def run(self, txt) -> str:
        result = self.agent.run(txt)
        return result

    def clear(self):
        self.agent.memory.clear()


bot = AgentBot()

block_css = """#col_container {width: 1000px; margin-left: auto; margin-right: auto;}
                #chatbot {height: 520px; overflow: auto;}"""

with gr.Blocks(css=block_css) as demo:
    gr.Markdown("<h3><center>Joyce你的私人情感咨询聊天机器人</center></h3>")
    gr.Markdown(
        """
         Joyce 心理咨询
        """
    )

    with gr.Row() as input_raw:
        with gr.Column(elem_id="col_container"):
            chatbot = gr.Chatbot([],
                                 elem_id="chatbot",
                                 label="Joyce",
                                 bubble_full_width=False,
                                 avatar_images=(None, (os.path.join(os.path.dirname(__file__), "avatar.png"))),
                                 )

            msg = gr.Textbox()

    with gr.Row():
        with gr.Column(scale=0.10, min_width=0):
            run = gr.Button("🏃‍♂️Run")
        with gr.Column(scale=0.10, min_width=0):
            clear = gr.Button("🔄Clear️")


    def respond(message, chat_history):
        # bot_message = random.choice(["How are you?", "I love you", "I'm very hungry"])
        bot_message = bot.run(message)
        regx = r'\b[\w-]+\.png'
        match_image = re.findall(regx, bot_message)
        chat_history.append((message, bot_message))
        if match_image:
            for image in match_image:
                image_path = os.path.join(SAVE_FOLDER, image)
                chat_history.append(
                    (None, (image_path,)),
                )
        return "", chat_history


    def clearMessage():
        # clear agent memory
        bot.clear()


    # execute action
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    run.click(respond, [msg, chatbot], [msg, chatbot])
    clear.click(clearMessage)
    clear.click(lambda: [], None, chatbot)

    gr.Examples(
        examples=["我最近情绪非常低迷",
                  "我心情很糟糕"],
        inputs=msg
    )

demo.launch()
