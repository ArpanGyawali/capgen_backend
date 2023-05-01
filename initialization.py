import os
import time

import av
import numpy as np
import torch
from huggingface_hub import hf_hub_download
from PIL import Image
from transformers import AutoModelForCausalLM, AutoProcessor
import copy



processor = None
model = None
device = None
git_model = None
pulchowk_model = None

def init():
    # instance of class transformers.AutoProcessor
    global processor

    # instance of class transformers.AutoModelForCausalLM
    global model

    # git model
    global git_model

    # pulchowk model
    global pulchowk_model

    if not os.path.exists("ml-models/git-base-vatex"):
        print("GIT Model downloading from huggingface")
        # ? Use this code to download the processor and model if you don't have it locally
        processor = AutoProcessor.from_pretrained("microsoft/git-base-vatex")
        git_model = AutoModelForCausalLM.from_pretrained("microsoft/git-base-vatex")
        # save them
        processor.save_pretrained("ml-models/git-base-vatex/processor")
        git_model.save_pretrained("ml-models/git-base-vatex/model")
        print("GIT Model downloading, loading and saving  from huggingface successful")
    else:
        print("GIT Model loading locally")
        # ? Use this code to load the processor and model if you have it locally
        processor = AutoProcessor.from_pretrained("ml-models/git-base-vatex/processor")
        git_model = AutoModelForCausalLM.from_pretrained("ml-models/git-base-vatex/model")
        print("GIT Model loading locally Success")



    #  load the pulchowk model.

    # update the git_model with the state of the custom pulchowk model 
        
    # Load the fine-tuned model
    if  os.path.exists("ml-models/pulchowk-model"):
        print("Pulchowk Model Loading...")
        model_name = "pulchowk-model.pkl" 
        pulchowk_model = copy.deepcopy(git_model)   

        pulchowk_model.load_state_dict(torch.load(f'ml-models/pulchowk-model/{model_name}'), strict=True)
        print("Pulchowk Model Loaded succesfully")

    # else:
    #     print("Pulchowk Model could not be loaded")

    #  default model is the git model 
    model = git_model


    # set seed for reproducability
    np.random.seed(40)
    global device
    device = torch.device("cuda")
    model.to(device)