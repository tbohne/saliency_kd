#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import argparse
from typing import List, Dict

import numpy as np
from openai import OpenAI

from saliency_kd.knowledge_graph_query_tool import KnowledgeGraphQueryTool
from saliency_kd.secret_config import OPENAI_API_KEY

INIT_PROMPT = "There is a number of signals:"
MODE_PROMPT_TS = ("\n\nIn the following separated lists of values, describe each list, i.e., signal, in a similar"
                  " fashion to the following symbolic description example.")
SYMBOLIC_EXAMPLE = ("\n\nexample_class: starting low, slowly but steadily going up to a positive peak or plateau,"
                    " afterwards it goes down again, very flat plateau, then going upwards to a noisy peak")
PROMPT_APPENDIX = ("\n\nDescribe them at roughly the same granularity as the example above (as a sentence, not bullet"
                   " points) - focus on the broad shape, not minor details, but mention the index of relevant peaks."
                   " However, avoid using absolute values in the descriptions (except indices).")


class LLMSymbolicDescGen:

    def __init__(self) -> None:
        """
        Initializes the symbolic description generator.
        """
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.kgqt = KnowledgeGraphQueryTool()

    def prompt_gpt(self, model: str, input_prompt: List[Dict]) -> str:
        """
        Prompt GPT model.

        :param model: LLM (OpenAI) model to be used
        :param input_prompt: input prompt(s)
        :return: parsed GPT response string
        """
        response = self.client.responses.create(
            # "o3-2025-04-16" (best, but expensive), "gpt-4o" (works), "gpt-4o-mini", "gpt-4.1-2025-04-14", "gpt-4.1"
            model=model,
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
    def get_medoids_ts(llm_input: str) -> np.ndarray:
        """
        Retrieves the medoids (time series) to generate textual descriptions for.

        :param llm_input: medoids for LLM description
        :return: numpy array of medoids
        """
        assert llm_input.endswith(".npy")
        return np.load(llm_input)

    def gen_prompt_ts(self, llm_input: str) -> List[Dict]:
        """
        Generates prompt for textual description of time series signals.

        :param llm_input: medoids for LLM description
        :return: prompt for GPT model
        """
        arr = self.get_medoids_ts(llm_input)
        medoid_lst = [" ".join([str(round(v, 2)) for v in c.tolist()]) for i, c in enumerate(arr)]
        str_medoids = "\n\n".join(f"signal {i + 1}:\n{c}" for i, c in enumerate(medoid_lst))
        prompt = INIT_PROMPT + MODE_PROMPT_TS + SYMBOLIC_EXAMPLE + PROMPT_APPENDIX + "\n\n" + str_medoids
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
    parser = argparse.ArgumentParser(description='generate textual class descriptions with LLM')
    parser.add_argument('--input', type=str, required=True, help='medoids for LLM description')
    parser.add_argument(
        "--model",
        choices=["o3-2025-04-16", "gpt-4o", "gpt-4.1", "gpt-4.1-2025-04-14", "gpt-4o-mini"],
        default="o3-2025-04-16",
        help="choose LLM model between o3-2025-04-16 (default), gpt-4o, gpt-4.1, gpt-4.1-2025-04-14 and gpt-4o-mini"
    )
    args = parser.parse_args()
    llm_sym_desc_gen = LLMSymbolicDescGen()
    output = llm_sym_desc_gen.prompt_gpt(args.model, llm_sym_desc_gen.gen_prompt_ts(args.input))
    print("output:", output)
