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

    def gpt_text_completion(self):
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[
                {"role": "user", "content": "write a haiku about ai"}
            ]
        )
        return completion.choices[0].message

    def get_centroid_img_base64(self):
        # read img as binary
        with open("img/llm_test_signal.png", "rb") as signal_img:
            return base64.b64encode(signal_img.read()).decode('utf-8')

    def gen_prompt(self):
        name_desc_pairs = self.kgqt.query_all_fault_desc()
        class_prompt = "\n".join([i[0] + ": " + i[1] for i in name_desc_pairs])

        print(INIT_PROMPT + class_prompt + PROMPT_APPENDIX + self.get_centroid_img_base64())


if __name__ == "__main__":
    llma = LLMAnalysis()
    llma.gen_prompt()
