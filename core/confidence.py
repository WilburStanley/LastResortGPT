import math

def calculate_confidence(token_logprobs: list) -> float:
    """Returns a confidence percentage (0-100) from a list of token log-probs."""
    if not token_logprobs:
        return 0.0

    valid_logprobs = []
    for logprob in token_logprobs:
        if logprob is None:
            continue
        if not isinstance(logprob, (int, float)):
            continue
        if logprob > 0:
            continue
        valid_logprobs.append(logprob)

    if not valid_logprobs:
        return 0.0

    average_logprob = sum(valid_logprobs) / len(valid_logprobs)

    try:
        probability = math.exp(average_logprob)
    except OverflowError:
        probability = 0.0

    confidence_percent = round(probability * 100, 1)
    confidence_percent = max(0.0, min(confidence_percent, 100.0))

    return confidence_percent