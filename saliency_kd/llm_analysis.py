#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import base64

from openai import OpenAI

from saliency_kd.knowledge_graph_query_tool import KnowledgeGraphQueryTool
from saliency_kd.secret_config import OPENAI_API_KEY

INIT_PROMPT = "There is a number of symbolic descriptions of signals:\n\n"
PROMPT_APPENDIX = ("\n\nIn the following img, describe each red signal in a similar fashion to the above symbolic descriptions. Describe the entire pathway for each, starting from the left until the end - at the same granularity as the examples above. Only then match each description to the best fitting case. Sometimes several might match in a way, it is important then to select the one that matches more precisely. Important: only match things that actually reasonably match; it is crucial to also identify signals that don't match any class. There also might be duplicates, i.e., more than one signal matching the same class. Finally, when the class description mentions that a signal keeps some value 'for a while' or something similar, it means that the peak looks more like a rectangle (many steps on the x-axis on its maximum, not its bottom), i.e., clearly distinct from a triangular sort of peak (few points on x-axis on its peak) where it goes up and down again.")
END_NOTE = "\nThe final line of the response string should be just the names of the predicted classes (comma separated) - exactly in the above notation."


class LLMAnalysis:

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.kgqt = KnowledgeGraphQueryTool()

    def prompt_gpt(self, input_prompt):
        # TODO: think about max_tokens argument (!)
        response = self.client.responses.create(
            # model="gpt-4.1",
            # model="gpt-4o", # works
            model="o3-2025-04-16", # --> best, but expensive
            # model="gpt-4o-mini",
            # max_tokens=300, # controlling costs (meant for responses)
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
        with open("img/centroids4llm.png", "rb") as signal_img:
            return base64.b64encode(signal_img.read()).decode('utf-8')

    @staticmethod
    def get_cluster_img_base64():
        # read img as binary
        with open("img/filtered_clusters.png", "rb") as signal_img:
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
                    # {
                    #     "type": "input_image",
                    #     "image_url": f"data:image/png;base64,{self.get_cluster_img_base64()}"
                    # },
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
