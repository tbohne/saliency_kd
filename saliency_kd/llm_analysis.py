#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import base64
from typing import List, Dict

import numpy as np
from openai import OpenAI

from saliency_kd.knowledge_graph_query_tool import KnowledgeGraphQueryTool
from saliency_kd.secret_config import OPENAI_API_KEY

INIT_PROMPT = "There is a number of symbolic descriptions of signals:\n\n"
MODE_PROMPT_IMG = ("\n\nIn the following img, describe each red signal in a similar fashion to the above symbolic"
                   " descriptions.")
MODE_PROMPT_TS = ("\n\nIn the following separated lists of values, describe each list, i.e., signal, in a similar"
                  " fashion to the above symbolic descriptions.")
PROMPT_APPENDIX = ("\n\nDescribe them at the same granularity as the examples above. Only then match each description"
                   " to the best fitting class. Sometimes several might match in a way, it is important then to select"
                   " the one that matches more precisely. If a case matches several classes very well, mention your"
                   " best guess and then mention the alternative in brackets as well. Important: only match things that"
                   " reasonably match; it is crucial to also identify signals that don't match any class. There also"
                   " might be duplicates, i.e., more than one signal matching the same class. Important: not every"
                   " detail must match; it should match the broad scheme best. Focus on the broad"
                   " shape, not minor details, but mention the index of relevant peaks. However, avoid using absolute"
                   " values in the descriptions (except indices). When it comes to the matching, the indices of peaks"
                   " should allow some tolerance for deviations; they should only roughly match.")
END_NOTE = ("\nThe final line of the response string should be just the names of the predicted classes (comma"
            " separated) - exactly in the above notation.")


class LLMAnalysis:

    def __init__(self) -> None:
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.kgqt = KnowledgeGraphQueryTool()

    def prompt_gpt(self, input_prompt: List[Dict]) -> str:
        """
        Prompt GPT model.

        :param input_prompt: input prompt(s)
        :return: parsed GPT response string
        """
        response = self.client.responses.create(
            # model="gpt-4.1",
            # model="gpt-4.1-2025-04-14",
            # model="gpt-4o",  # works
            model="o3-2025-04-16",  # --> best, but expensive
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
        # print(response.usage.input_tokens)
        # print(response.usage.output_tokens)
        # print(response.usage.total_tokens)

        return response.output_text.split("\n")[-1]

    @staticmethod
    def get_centroid_img_base64() -> str:
        """
        Retrieves the centroid image as base64-coded string.

        :return: centroid image as base64-coded string
        """
        # read img as binary
        with open("centroids4llm.png", "rb") as signal_img:
            return base64.b64encode(signal_img.read()).decode('utf-8')

    @staticmethod
    def get_cluster_img_base64() -> str:
        """
        Retrieves the cluster image as base64-coded string.

        :return: cluster image as base64-coded string
        """
        # read img as binary
        with open("img/filtered_clusters.png", "rb") as signal_img:
            return base64.b64encode(signal_img.read()).decode('utf-8')

    @staticmethod
    def get_centroids_ts() -> np.ndarray:
        """
        Retrieves the centroid time series as numpy array.

        :return: centroid time series
        """
        return np.load("centroids4llm.npy")

    def gen_prompt_img(self) -> List[Dict]:
        """
        Generates prompt for textual description of input image.

        :return: prompt for GPT model
        """
        name_desc_pairs = self.kgqt.query_all_fault_desc()
        class_prompt = "\n".join([i[0] + ": " + i[1] for i in name_desc_pairs])
        prompt = INIT_PROMPT + class_prompt + MODE_PROMPT_IMG + PROMPT_APPENDIX + END_NOTE
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

    def gen_prompt_ts(self) -> List[Dict]:
        """
        Generates prompt for textual description of time series signals.

        :return: prompt for GPT model
        """
        name_desc_pairs = self.kgqt.query_all_fault_desc()
        class_prompt = "\n".join([i[0] + ": " + i[1] for i in name_desc_pairs])
        arr = self.get_centroids_ts()
        centroid_lst = [" ".join([str(round(v, 2)) for v in c.tolist()]) for i, c in enumerate(arr)]
        str_centroids = "\n\n".join(f"signal {i + 1}:\n{c}" for i, c in enumerate(centroid_lst))
        prompt = INIT_PROMPT + class_prompt + MODE_PROMPT_TS + PROMPT_APPENDIX + END_NOTE + "\n\n" + str_centroids
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
                ]
            }
        ]


if __name__ == "__main__":
    llma = LLMAnalysis()
    # predicted_class = llma.prompt_gpt(llma.gen_prompt_img())
    predicted_class = llma.prompt_gpt(llma.gen_prompt_ts())
    print("pred class:", predicted_class)

    # retrieve additional symbolic information
    kgqt = KnowledgeGraphQueryTool()
    print("additional symbolic information obtained from KG:")
    print(kgqt.query_fault_information_by_name(predicted_class))
