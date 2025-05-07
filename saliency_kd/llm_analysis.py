#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from openai import OpenAI

from saliency_kd.secret_config import OPENAI_API_KEY


class LLMAnalysis:

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def gpt_text_completion(self):
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[
                {"role": "user", "content": "write a haiku about ai"}
            ]
        )
        return completion.choices[0].message


if __name__ == "__main__":
    llma = LLMAnalysis()
    print(llma.gpt_text_completion())
