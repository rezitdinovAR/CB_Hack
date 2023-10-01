from fastapi import APIRouter, File, UploadFile
from models import Answer
from utils import get_file, get_transcription, get_bert_extractive_summarizer
from stt_summarization import Summarizer
from video_to_text import VideoEncode


router = APIRouter()
stt_summarizer = Summarizer(
    model_path="/home/asr/projects/kaitube/models/IlyaGusev-mbart_ru_sum_gazeta-finetune-1024-gas-video/checkpoint-110/",
    model_max_length=2048
)
video_to_text = VideoEncode()


@router.post('/listening/', response_model=Answer)
async def listening(video: UploadFile = File(...), transcription: UploadFile = File(...)) -> dict:
    '''Аудирование - изучение татарских слов'''

    video_message = get_file(video)
    transcription_message = get_file(transcription)
    prefix = "summarize: "

    transcription_text = get_transcription('app/files/' + transcription.filename)
    summarization_transcription = get_bert_extractive_summarizer(transcription_text)['summary'][:1000]

    video_text = video_to_text.predict('app/files/' + video.filename)
    video_transcription = get_bert_extractive_summarizer(video_text)['summary'][:1000]

    summarization = stt_summarizer.predict(prefix + summarization_transcription + '<tab>' + video_transcription)

    return {
        'video': video.filename,
        'transcription': transcription.filename,
        "video_message": video_message,
        'transcription_message': transcription_message,
        'description': summarization,
        'url': "Тут будет ссылка на файл"
    }
