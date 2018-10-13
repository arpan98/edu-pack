import fetch_images
import fetch_keywords

import nltk
from moviepy.editor import *
from gtts import gTTS

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

# fetch_images.run("dog",0)
# print(fetch_keywords.run("Aldol condensation reaction consists of combination of aldehydes and alcohol."))

text = "Photosynthesis is the process by which plants, some bacteria and some protistans use the energy from sunlight to produce glucose from carbon dioxide and water. This glucose can be converted into pyruvate which releases adenosine triphosphate (ATP) by cellular respiration. Oxygen is also formed."
# text = "Homeostasis is the state of steady internal conditions maintained by living things.[1] This dynamic state of equilibrium is the condition of optimal functioning for the organism and includes many variables, such as body temperature and fluid balance, being kept within certain pre-set limits (homeostatic range). Other variables include the pH of extracellular fluid, the concentrations of sodium, potassium and calcium ions, as well as that of the blood sugar level, and these need to be regulated despite changes in the environment, diet, or level of activity. Each of these variables is controlled by one or more regulators or homeostatic mechanisms, which together maintain life."

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
sentences = tokenizer.tokenize(text)
print(sentences)

word_list = []
text_clip_list = []
video_clip_list = []
audio_clip_list = []

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
	
	audio_clip = gTTS(text=sentences[i], lang='en', slow=False)
	audio_clip.save('sounds/'+str(i)+'.mp3')
	print(sentences[i] + "audio file saved")
	
	current_audio_clip=AudioFileClip('sounds/'+str(i)+'.mp3')
	audio_clip_list.append(current_audio_clip)

	#TODO modify time duration
	current_text_clip = TextClip(format_text(sentences[i]),font='Montserrat',fontsize=25,color='white',bg_color='black',stroke_width=5).set_duration(current_audio_clip.duration)
	text_clip_list.append(current_text_clip)

	savepath = fetch_images.run(current_keyword,i)
	print(savepath)
	current_video_clip = ImageClip(savepath).set_opacity(1).set_duration(current_audio_clip.duration).set_fps(30).crossfadein(0.5)
	video_clip_list.append(current_video_clip)

text_clip=concatenate_videoclips(text_clip_list).set_position('bottom')
video_clip=concatenate_videoclips(video_clip_list, method='compose').set_position(('center','top'))
result=CompositeVideoClip([video_clip,text_clip])

audio_clip=concatenate_audioclips(audio_clip_list)
result_with_audio=result.set_audio(audio_clip)

print("Saving Video!")
result_with_audio.write_videofile('videos/0.mp4',codec='libx264',fps=30)

print("Done!")