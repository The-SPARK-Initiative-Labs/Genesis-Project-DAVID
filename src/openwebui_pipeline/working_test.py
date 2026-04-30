"""
title: Working Test Pipeline
author: test
version: 1.0.0
description: Correctly formatted pipeline
"""

from typing import List, Union, Generator, Iterator
from pydantic import BaseModel

class Pipeline:
    class Valves(BaseModel):
        pass

    def __init__(self):
        self.name = "Working Test Pipeline"

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        
        return f"Echo: {user_message}"
