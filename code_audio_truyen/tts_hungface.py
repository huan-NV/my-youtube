from transformers import AutoProcessor, AutoModel, AutoTokenizer
import soundfile as sf
import torch
import numpy as np

device = "cuda"
model_id = "DragonLineageAI/Vi-SparkTTS-0.5B"
processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
model = AutoModel.from_pretrained(model_id, trust_remote_code=True).eval()
processor.model = model
 
prompt_audio_path = "Z:/download/ttsmaker-file-2025-4-25-21-11-22.mp3" # CHANGE TO YOUR ACTUAL PATH
prompt_transcript = "text corresponding to prompt audio" # Optional
text_input = "xin chào mọi người chúng tôi là Nguyễn Công Tú Anh và Chu Văn An đến từ dragonlineageai"
 
inputs = processor(
    text=text_input.lower(),
    prompt_speech_path=prompt_audio_path,
    prompt_text=prompt_transcript,
    return_tensors="pt"
).to(device)
global_tokens_prompt = inputs.pop("global_token_ids_prompt", None)
 
with torch.no_grad():
    output_ids = model.generate(
        **inputs,
        max_new_tokens=3000,
        do_sample=True,
        temperature=0.8,
        top_k=50,
        top_p=0.95,
        eos_token_id=processor.tokenizer.eos_token_id,  
        pad_token_id=processor.tokenizer.pad_token_id  
    )
       
output_clone = processor.decode(
    generated_ids=output_ids,
    global_token_ids_prompt=global_tokens_prompt,
    input_ids_len=inputs["input_ids"].shape[-1]
)
 
sf.write("output_cloned.wav", output_clone["audio"], output_clone["sampling_rate"])
