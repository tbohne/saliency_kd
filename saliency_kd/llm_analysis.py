#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import base64

from openai import OpenAI

from saliency_kd.knowledge_graph_query_tool import KnowledgeGraphQueryTool
from saliency_kd.secret_config import OPENAI_API_KEY

INIT_PROMPT = "There is a number of symbolic descriptions of signals:\n\n"
PROMPT_APPENDIX = "\n\nDescribe the following signal img in a similar fashion, then match the description to the best fitting case: "
END_NOTE = "\nThe final line of the response string should be just the name of the predicted class - exactly in the above notation."


class LLMAnalysis:

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.kgqt = KnowledgeGraphQueryTool()

    def prompt_gpt(self, input_prompt):
        # TODO: think about max_tokens argument (!)
        response = self.client.responses.create(
            # model="gpt-4.1",
            model="gpt-4o",
            # model="gpt-4o-mini",
            # max_tokens=300,  # controlling costs (meant for responses)
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

        return response.output_text.split("\n")[-1]

    @staticmethod
    def get_centroid_img_base64():
        # read img as binary
        with open("img/llm_test_signal.png", "rb") as signal_img:
            return base64.b64encode(signal_img.read()).decode('utf-8')

    def gen_prompt(self):
        name_desc_pairs = self.kgqt.query_all_fault_desc()
        class_prompt = "\n".join([i[0] + ": " + i[1] for i in name_desc_pairs])
        prompt = INIT_PROMPT + class_prompt + PROMPT_APPENDIX + END_NOTE
        print("-----------------------------------------------------")
        print("prompt..\n", prompt)
        print("-----------------------------------------------------")
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{self.get_centroid_img_base64()}"
                    }
                ]
            }
        ]


if __name__ == "__main__":
    llma = LLMAnalysis()
    # print(llma.gen_prompt())
    predicted_class = llma.prompt_gpt(llma.gen_prompt())
    print("pred class:", predicted_class)

    # retrieve additional symbolic information
    kgqt = KnowledgeGraphQueryTool()
    print("additional symbolic information obtained from KG:")
    print(kgqt.query_fault_information_by_name(predicted_class))
