import initialization
import numpy as np
from huggingface_hub import hf_hub_download
import time
import av

initialization.init()

# print(initialization.processor)

processor = initialization.processor
model = initialization.model
device = initialization.device



def read_video_pyav(container, indices):
    """
    Decode the video with PyAV decoder.
    Args:
        container (`av.container.input.InputContainer`): PyAV container.
        indices (`List[int]`): List of frame indices to decode.
    Returns:
        result (np.ndarray): np array of decoded frames of shape (num_frames, height, width, 3).
    """
    frames = []
    container.seek(0)
    start_index = indices[0]
    end_index = indices[-1]
    for i, frame in enumerate(container.decode(video=0)):
        if i > end_index:
            break
        if i >= start_index and i in indices:
            frames.append(frame)
    return np.stack([x.to_ndarray(format="rgb24") for x in frames])


def sample_frame_indices(clip_len, frame_sample_rate, seg_len):
    converted_len = int(clip_len * frame_sample_rate)  # 24

    # end_idx = np.random.randint(converted_len, seg_len)# 24 ... 197
    # start_idx = end_idx - converted_len #0 , 197-24
    # indices = np.linspace(start_idx, end_idx, num=clip_len)
    indices = np.linspace(0, seg_len, num=clip_len)
    indices = np.clip(indices, 0, seg_len - 1).astype(np.int64)
    return indices


# load video
# file_path = hf_hub_download(
#     repo_id="nielsr/video-demo", filename="eating_spaghetti.mp4", repo_type="dataset"
# )
file_path = "check/video3.mp4"
container = av.open(file_path)

# sample frames
num_frames = model.config.num_image_with_embedding
indices = sample_frame_indices(
    clip_len=num_frames, frame_sample_rate=4, seg_len=container.streams.video[0].frames
)
frames = read_video_pyav(container, indices)


start = time.time()
pixel_values = processor(images=list(frames), return_tensors="pt").pixel_values


# frames = torch.tensor(frames).to(device)
pixel_values = pixel_values.to(device)


# generated_ids = model.generate(pixel_values=pixel_values, max_length=20)

generated_ids = model.generate(pixel_values=pixel_values, max_length=50)
end = time.time()
print(end - start)

print(
    "Generated caption:",
    processor.batch_decode(generated_ids, skip_special_tokens=True),
)
