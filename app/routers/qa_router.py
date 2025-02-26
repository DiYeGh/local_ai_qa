from fastapi import APIRouter, HTTPException
from app.services.ai_service import AIService
from app.models.schemas import QuestionRequest, AnswerResponse

router = APIRouter()
ai_service = AIService()

@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest) -> AnswerResponse:
    """
    问答接口
    """
    try:
        # 调用AI服务生成答案
        result = await ai_service.generate_answer(request.question)
        
        return AnswerResponse(
            answer=result["answer"],
            source_chunks=result["source_chunks"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
