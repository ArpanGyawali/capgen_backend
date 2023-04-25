import os
import time

import av
import numpy as np
import torch
from huggingface_hub import hf_hub_download
from PIL import Image
from transformers import AutoModelForCausalLM, AutoProcessor

processor = None
model = None
device = None

def init():
    # instance of class transformers.AutoProcessor
    global processor

    # instance of class transformers.AutoModelForCausalLM
    global model

    if not os.path.exists("ml-models/git-base-vatex"):
        print("Model downloading from huggingface")
        # ? Use this code to download the processor and model if you don't have it locally
        processor = AutoProcessor.from_pretrained("microsoft/git-base-vatex")
        model = AutoModelForCausalLM.from_pretrained("microsoft/git-base-vatex")
        # save them
        processor.save_pretrained("ml-models/git-base-vatex/processor")
        model.save_pretrained("ml-models/git-base-vatex/model")
    else:
        print("Model loading locally")
        # ? Use this code to load the processor and model if you have it locally
        processor = AutoProcessor.from_pretrained("ml-models/git-base-vatex/processor")
        model = AutoModelForCausalLM.from_pretrained("ml-models/git-base-vatex/model")


    # set seed for reproducability
    np.random.seed(40)
    global device
    device = torch.device("cuda")
    model.to(device)