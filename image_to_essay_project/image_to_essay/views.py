from django.shortcuts import render, redirect
from .forms import ImageEssayForm
from .models import ImageEssay
import openai
from PIL import Image  
import warnings  
import torch, joblib


# Load the saved joblib files 
model = joblib.load("image_to_essay/vision_encoder_decoder_model.joblib") 
feature_extractor = joblib.load("image_to_essay/vit_feature_extractor.joblib")
tokenizer = joblib.load("image_to_essay/auto_tokenizer.joblib")


# Suppress the specific warning
warnings.filterwarnings("ignore", message=".*'attention_mask' since your input_ids may be padded.*")


# Define the device to use (GPU if available, otherwise CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)  # Move the model to the device


# Define the maximum length and number of beams for caption generation
max_length = 16
num_beams = 4


def generate_essay(image,user_input,option):
    try:
        # Open the uploaded image using Pillow (PIL)
        img = Image.open(image)
        # Ensure that the image is in a supported format (e.g., JPEG, PNG)
        if img.format not in ['JPEG', 'PNG']:
            raise ValueError("Unsupported image format")

        # Perform OCR on the image

        # Load and preprocess the image
        image = img
        if image.mode != "RGB":
          image = image.convert(mode="RGB")

        # Extract features from the image
        pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(device)  # Move the image tensor to the device

        # Generate captions without specifying attention_mask
        gen_kwargs = {
            "max_length": max_length,
            "num_beams": num_beams,
        }
        output_ids = model.generate(pixel_values, **gen_kwargs)

        # Decode and return the captions
        preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        preds = [pred.strip() for pred in preds]
        
        openai.api_key = 'API KEY'                     #Enter the API key  
        messages = [ {"role": "system", "content": "You are a intelligent assistant."} ]
        #message = 'A Picture containing' + preds[0] + 'give some tips to improve the picture considering its pose, color mode, background, dress also provide a proper imaginary scene for this picture'
        print("\n"+preds[0])
        message = 'The script of a movie is'+ user_input +'the scene is'+ preds[0] +'the character in the scene is'+ option +'give 5 imaginary best situational scenes in an elaborate manner as per the script. Also provide best costume, location, timing to shoot this shot. (Print the side headings in Bold)'
        if message:
          messages.append({"role": "user", "content": message})
        chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
        )
        reply = chat.choices[0].message.content
        return reply

    except Exception as e:
        # Handle any exceptions that may occur during image processing
        print(f"Error processing image: {e}")
        return "Error processing image"

def upload_image(request):
    if request.method == 'POST':
        form = ImageEssayForm(request.POST, request.FILES)
        if form.is_valid():
            user_input = request.POST.get('user_input')  # Fetch the user input
            option = request.POST.get('option')  # Fetch the selected option
            instance = form.save(commit=False)
            instance.essay = generate_essay(instance.image,user_input,option)
            instance.save()
            return redirect('essay_detail', pk=instance.pk)
    else:
        form = ImageEssayForm()
    return render(request, 'upload_image.html', {'form': form})

def essay_detail(request, pk):
    essay = ImageEssay.objects.get(pk=pk)
    return render(request, 'essay_detail.html', {'essay': essay})
