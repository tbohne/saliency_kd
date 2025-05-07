#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import base64

from openai import OpenAI

from saliency_kd.knowledge_graph_query_tool import KnowledgeGraphQueryTool
from saliency_kd.secret_config import OPENAI_API_KEY

INIT_PROMPT = "There is a number of symbolic descriptions of signals:\n\n"
PROMPT_APPENDIX = "\n\nDescribe the following base64 coded signal img in a similar fashion, then match the description to the best fitting case: "


class LLMAnalysis:

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.kgqt = KnowledgeGraphQueryTool()

    def prompt_gpt(self, input_prompt):
        # TODO: think about max_tokens argument (!)
        response = self.client.responses.create(
            # model="gpt-4.1",
            model="gpt-4o-mini",
            input=input_prompt
        )
        print("response..")
        print(response.id)
        print(response.model)
        print(response.output_text)
        print(response.temperature)
        print(response.max_output_tokens)
        print(response.usage)

        # TODO: test those
        # print(response.usage.input_tokens)
        # print(response.usage.output_tokens)
        # print(response.usage.total_tokens)

        return response.output_text

    @staticmethod
    def get_centroid_img_base64():
        # read img as binary
        with open("img/llm_test_signal.png", "rb") as signal_img:
            return base64.b64encode(signal_img.read()).decode('utf-8')

    def gen_prompt(self):
        name_desc_pairs = self.kgqt.query_all_fault_desc()
        class_prompt = "\n".join([i[0] + ": " + i[1] for i in name_desc_pairs])
        prompt = INIT_PROMPT + class_prompt + PROMPT_APPENDIX + self.get_centroid_img_base64()
        print("-----------------------------------------------------")
        print("prompt..\n", prompt)
        print("-----------------------------------------------------")
        return [
            # TODO: might need to separate img and text
            {
                "role": "user",
                "content": prompt
            }
        ]


if __name__ == "__main__":
    llma = LLMAnalysis()
    # print(llma.gen_prompt())
    llma.prompt_gpt(llma.gen_prompt())
