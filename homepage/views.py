from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.staticfiles.templatetags.staticfiles import static

import json

from homepage import fetch_images
from homepage import fetch_keywords

import nltk
from moviepy.editor import *
from gtts import gTTS

import random

def format_text(string): #break in to lines to fit the screen
	words=string.split()
	output=''
	buffer_string=''
	for w in words:
		if(len(buffer_string)<40):
			buffer_string+=w+' '
		else:
			output+=buffer_string+'\n'
			buffer_string=w+' '
	output+=buffer_string
	return output

# Create your views here.
def show_homepage(request):
	return render(request, 'homepage/homepage.html')

@csrf_exempt
def text_to_video(request):
	if request.method == "POST":
		text = request.POST['text']
		print(request.POST['text'])
		tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
		sentences = tokenizer.tokenize(text)
		print(sentences)

		word_list = []
		text_clip_list = []
		video_clip_list = []
		# audio_clip_list = []

		for i in range(len(sentences)):
			#TODO add try catch
			keywords = fetch_keywords.run(sentences[i])
			print(keywords)
			j = 0
			current_keyword = keywords[j]["text"]
			while current_keyword in word_list:
				j+=1
				current_keyword = keywords[j]["text"]
			word_list.append(current_keyword)
			
			# audio_clip = gTTS(text=sentences[i], lang='en', slow=False)
			# audio_clip.save('sounds/'+str(i)+'.mp3')
			# print(sentences[i] + "audio file saved")
			
			# current_audio_clip=AudioFileClip('sounds/'+str(i)+'.mp3')
			# audio_clip_list.append(current_audio_clip)

			#TODO modify time duration
			current_text_clip = TextClip(format_text(sentences[i]),font='Montserrat',fontsize=25,color='white',bg_color='black',stroke_width=5).set_duration(len(sentences[i]) * 0.08)
			text_clip_list.append(current_text_clip)

			savepath = fetch_images.run(current_keyword,i,num_images=3)
			print(savepath)
			current_video_clip = ImageClip(savepath).set_opacity(1).set_duration(len(sentences[i]) * 0.08).set_fps(30).crossfadein(0.5)
			video_clip_list.append(current_video_clip)

		text_clip=concatenate_videoclips(text_clip_list).set_position('bottom')
		video_clip=concatenate_videoclips(video_clip_list, method='compose').set_position(('center','top'))
		result=CompositeVideoClip([video_clip,text_clip])

		# audio_clip=concatenate_audioclips(audio_clip_list)
		# result_with_audio=result.set_audio(audio_clip)

		print("Saving Video!")
		result.write_videofile('homepage/static/homepage/0.mp4',codec='libx264',fps=10,audio=False,threads=4,preset='ultrafast')
		print("Done!")

		question_answers = []
		if (len(sentences)<=3) :
			for i in range(len(sentences)):
				question_answers.append({"question":sentences[i].replace(word_list[i],"__________"),"answer":word_list[i]})
		else :
			values = random.sample(range(0, len(sentences)-1), 3)
			for i in range(3):
				question_answers.append({"question":sentences[values[i]].replace(word_list[values[i]],"__________"),"answer":word_list[values[i]]})

		print(question_answers)
		return HttpResponse(json.dumps(question_answers), content_type="application/json")