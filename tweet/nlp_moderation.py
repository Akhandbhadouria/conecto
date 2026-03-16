"""
AI-Powered NLP Comment Moderation System
=========================================
Uses a pre-trained LinearSVC model (via alt-profanity-check) to detect
toxic, offensive, or abusive language in user comments in near real-time.

NLP Processing Pipeline:
  1. Convert text to lowercase
  2. Remove punctuation and special characters
  3. Tokenize text
  4. Apply TF-IDF vectorization
  5. Run the trained classification model (LinearSVC)

The model returns:  1 = offensive/abusive,  0 = safe
"""
import re
import logging
from profanity_check import predict
from .models import ModerationLog

logger = logging.getLogger(__name__)


def preprocess_text(text):
    """
    Basic NLP preprocessing:
      - lowercase
      - strip punctuation / special chars
      - collapse whitespace
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)   # remove punctuation
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def check_comment_text(user, raw_text):
    """
    Run AI moderation on a comment.

    Args:
        user:     Django User instance
        raw_text: the raw comment string

    Returns:
        dict  {'is_safe': bool, 'prediction': str, 'message': str}
    """
    try:
        cleaned = preprocess_text(raw_text)

        # Model prediction — runs instantly (~1 ms)
        predictions = predict([cleaned])
        is_offensive = predictions[0] == 1

        prediction_label = 'abusive' if is_offensive else 'safe'

        # ---- Moderation Log (always logged) ----
        ModerationLog.objects.create(
            user=user,
            comment_text=raw_text,
            prediction=prediction_label,
        )

        if is_offensive:
            logger.warning(
                f"ABUSIVE comment blocked | user='{user.username}' | text='{raw_text[:80]}'"
            )
            return {
                'is_safe': False,
                'prediction': 'abusive',
                'message': (
                    '🛡️ Your comment violates community guidelines. '
                    'This action has been recorded.'
                ),
            }

        return {
            'is_safe': True,
            'prediction': 'safe',
            'message': 'Comment is safe.',
        }

    except Exception as exc:
        logger.error(f"NLP moderation error: {exc}", exc_info=True)
        # Fail-open so a model crash doesn't break the user experience
        return {
            'is_safe': True,
            'prediction': 'error',
            'message': 'Moderation passed (fallback).',
        }
