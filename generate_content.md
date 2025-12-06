Based on the latest documentation from https://ai.google.dev/api/generate-content, here are the JSON representations of the types.

Request Body
GenerateContentRequest

The top-level request body for the generateContent method.[1]

code
JSON
download
content_copy
expand_less
{
  "contents": [
    {
      "object": "Content"
    }
  ],
  "tools": [
    {
      "object": "Tool"
    }
  ],
  "toolConfig": {
    "object": "ToolConfig"
  },
  "safetySettings": [
    {
      "object": "SafetySetting"
    }
  ],
  "systemInstruction": {
    "object": "Content"
  },
  "generationConfig": {
    "object": "GenerationConfig"
  },
  "cachedContent": "string"
}
Content

The base unit of structured text and media.[1]

code
JSON
download
content_copy
expand_less
{
  "parts": [
    {
      "object": "Part"
    }
  ],
  "role": "string"
}
Part

A datatype containing media.[1] It is a union type; typically only one field is set.[1]

code
JSON
download
content_copy
expand_less
{
  "text": "string",
  "inlineData": {
    "mimeType": "string",
    "data": "string (base64 encoded)"
  },
  "functionCall": {
    "name": "string",
    "args": {
      "object": "object"
    }
  },
  "functionResponse": {
    "name": "string",
    "response": {
      "object": "object"
    }
  },
  "fileData": {
    "mimeType": "string",
    "fileUri": "string"
  },
  "executableCode": {
    "language": "LANGUAGE_PYTHON",
    "code": "string"
  },
  "codeExecutionResult": {
    "outcome": "OUTCOME_OK | OUTCOME_FAILED | OUTCOME_DEADLINE_EXCEEDED",
    "output": "string"
  }
}
GenerationConfig

Configuration options for model generation and outputs.[1]

code
JSON
download
content_copy
expand_less
{
  "stopSequences": [
    "string"
  ],
  "responseMimeType": "string",
  "responseSchema": {
    "object": "Schema"
  },
  "responseJsonSchema": {
    "object": "Value"
  },
  "responseModalities": [
    "MODALITY_UNSPECIFIED | TEXT | IMAGE | AUDIO"
  ],
  "candidateCount": "integer",
  "maxOutputTokens": "integer",
  "temperature": "number",
  "topP": "number",
  "topK": "integer",
  "seed": "integer",
  "presencePenalty": "number",
  "frequencyPenalty": "number",
  "responseLogprobs": "boolean",
  "logprobs": "integer",
  "enableEnhancedCivicAnswers": "boolean",
  "speechConfig": {
    "object": "SpeechConfig"
  },
  "thinkingConfig": {
    "object": "ThinkingConfig"
  },
  "imageConfig": {
    "object": "ImageConfig"
  },
  "mediaResolution": "MEDIA_RESOLUTION_UNSPECIFIED | MEDIA_RESOLUTION_LOW | MEDIA_RESOLUTION_MEDIUM | MEDIA_RESOLUTION_HIGH"
}
SafetySetting

Specifies the safety settings for the request.

code
JSON
download
content_copy
expand_less
{
  "category": "HARM_CATEGORY_HATE_SPEECH | HARM_CATEGORY_SEXUALLY_EXPLICIT | HARM_CATEGORY_DANGEROUS_CONTENT | HARM_CATEGORY_HARASSMENT | HARM_CATEGORY_CIVIC_INTEGRITY",
  "threshold": "HARM_BLOCK_THRESHOLD_UNSPECIFIED | BLOCK_LOW_AND_ABOVE | BLOCK_MEDIUM_AND_ABOVE | BLOCK_ONLY_HIGH | BLOCK_NONE | OFF"
}
Tool

Defines tools the model may use.[1]

code
JSON
download
content_copy
expand_less
{
  "functionDeclarations": [
    {
      "name": "string",
      "description": "string",
      "parameters": {
        "object": "Schema"
      }
    }
  ],
  "googleSearchRetrieval": {
    "dynamicRetrievalConfig": {
      "mode": "MODE_UNSPECIFIED | MODE_DYNAMIC",
      "dynamicThreshold": "number"
    }
  },
  "codeExecution": {}
}
ToolConfig

Configuration for the tools.[1]

code
JSON
download
content_copy
expand_less
{
  "functionCallingConfig": {
    "mode": "MODE_UNSPECIFIED | AUTO | ANY | NONE",
    "allowedFunctionNames": [
      "string"
    ]
  }
}
SpeechConfig

Configuration for speech generation.[1]

code
JSON
download
content_copy
expand_less
{
  "voiceConfig": {
    "prebuiltVoiceConfig": {
      "voiceName": "string"
    }
  },
  "multiSpeakerVoiceConfig": {
    "speakerVoiceConfigs": [
      {
        "speaker": "string",
        "voiceConfig": {
           "prebuiltVoiceConfig": {
             "voiceName": "string"
           }
        }
      }
    ]
  },
  "languageCode": "string"
}
ThinkingConfig

Configuration for thinking features (Gemini 3+).

code
JSON
download
content_copy
expand_less
{
  "includeThoughts": "boolean",
  "thinkingBudget": "integer",
  "thinkingLevel": "THINKING_LEVEL_UNSPECIFIED | LOW | HIGH"
}
ImageConfig

Configuration for image generation.[1]

code
JSON
download
content_copy
expand_less
{
  "aspectRatio": "string",
  "imageSize": "string"
}
Response Body
GenerateContentResponse

The top-level response object.[1]

code
JSON
download
content_copy
expand_less
{
  "candidates": [
    {
      "object": "Candidate"
    }
  ],
  "promptFeedback": {
    "object": "PromptFeedback"
  },
  "usageMetadata": {
    "object": "UsageMetadata"
  },
  "modelVersion": "string",
  "responseId": "string"
}
Candidate

A response candidate generated from the model.[1]

code
JSON
download
content_copy
expand_less
{
  "content": {
    "object": "Content"
  },
  "finishReason": "STOP | MAX_TOKENS | SAFETY | RECITATION | LANGUAGE | OTHER | BLOCKLIST | PROHIBITED_CONTENT | SPII | MALFORMED_FUNCTION_CALL | IMAGE_SAFETY | IMAGE_PROHIBITED_CONTENT | IMAGE_OTHER | NO_IMAGE | IMAGE_RECITATION | UNEXPECTED_TOOL_CALL | TOO_MANY_TOOL_CALLS | MISSING_THOUGHT_SIGNATURE",
  "safetyRatings": [
    {
      "object": "SafetyRating"
    }
  ],
  "citationMetadata": {
    "object": "CitationMetadata"
  },
  "tokenCount": "integer",
  "groundingAttributions": [
    {
      "object": "GroundingAttribution"
    }
  ],
  "groundingMetadata": {
    "object": "GroundingMetadata"
  },
  "avgLogprobs": "number",
  "logprobsResult": {
    "object": "LogprobsResult"
  },
  "urlContextMetadata": {
    "object": "UrlContextMetadata"
  },
  "index": "integer",
  "finishMessage": "string"
}
PromptFeedback

Feedback metadata for the prompt.

code
JSON
download
content_copy
expand_less
{
  "blockReason": "BLOCK_REASON_UNSPECIFIED | SAFETY | OTHER | BLOCKLIST | PROHIBITED_CONTENT | IMAGE_SAFETY",
  "safetyRatings": [
    {
      "object": "SafetyRating"
    }
  ]
}
UsageMetadata

Token usage metadata.

code
JSON
download
content_copy
expand_less
{
  "promptTokenCount": "integer",
  "cachedContentTokenCount": "integer",
  "candidatesTokenCount": "integer",
  "toolUsePromptTokenCount": "integer",
  "thoughtsTokenCount": "integer",
  "totalTokenCount": "integer",
  "promptTokensDetails": [
    {
      "object": "ModalityTokenCount"
    }
  ],
  "cacheTokensDetails": [
    {
      "object": "ModalityTokenCount"
    }
  ],
  "candidatesTokensDetails": [
    {
      "object": "ModalityTokenCount"
    }
  ],
  "toolUsePromptTokensDetails": [
    {
      "object": "ModalityTokenCount"
    }
  ]
}
ModalityTokenCount
code
JSON
download
content_copy
expand_less
{
  "modality": "MODALITY_UNSPECIFIED | TEXT | IMAGE | VIDEO | AUDIO | DOCUMENT",
  "tokenCount": "integer"
}
SafetyRating
code
JSON
download
content_copy
expand_less
{
  "category": "HARM_CATEGORY_HATE_SPEECH | HARM_CATEGORY_SEXUALLY_EXPLICIT | HARM_CATEGORY_DANGEROUS_CONTENT | HARM_CATEGORY_HARASSMENT",
  "probability": "HARM_PROBABILITY_UNSPECIFIED | NEGLIGIBLE | LOW | MEDIUM | HIGH",
  "blocked": "boolean"
}

[1]

CitationMetadata
code
JSON
download
content_copy
expand_less
{
  "citationSources": [
    {
      "startIndex": "integer",
      "endIndex": "integer",
      "uri": "string",
      "license": "string"
    }
  ]
}
GroundingMetadata

Metadata returned when grounding is enabled.[1]

code
JSON
download
content_copy
expand_less
{
  "groundingChunks": [
    {
      "object": "GroundingChunk"
    }
  ],
  "groundingSupports": [
    {
      "object": "GroundingSupport"
    }
  ],
  "webSearchQueries": [
    "string"
  ],
  "searchEntryPoint": {
    "renderedContent": "string",
    "sdkBlob": "string"
  },
  "retrievalMetadata": {
    "googleSearchDynamicRetrievalScore": "number"
  },
  "googleMapsWidgetContextToken": "string"
}
GroundingChunk
code
JSON
download
content_copy
expand_less
{
  "web": {
    "uri": "string",
    "title": "string"
  },
  "retrievedContext": {
    "uri": "string",
    "title": "string",
    "text": "string",
    "fileSearchStore": "string"
  },
  "maps": {
    "uri": "string",
    "title": "string",
    "text": "string",
    "placeId": "string",
    "placeAnswerSources": {
      "reviewSnippets": [
        {
          "reviewId": "string",
          "googleMapsUri": "string",
          "title": "string"
        }
      ]
    }
  }
}
GroundingSupport
code
JSON
download
content_copy
expand_less
{
  "groundingChunkIndices": [
    "integer"
  ],
  "confidenceScores": [
    "number"
  ],
  "segment": {
    "partIndex": "integer",
    "startIndex": "integer",
    "endIndex": "integer",
    "text": "string"
  }
}
GroundingAttribution
code
JSON
download
content_copy
expand_less
{
  "sourceId": {
    "groundingPassage": {
      "passageId": "string",
      "partIndex": "integer"
    },
    "semanticRetrieverChunk": {
      "source": "string",
      "chunk": "string"
    }
  },
  "content": {
    "object": "Content"
  }
}
LogprobsResult
code
JSON
download
content_copy
expand_less
{
  "topCandidates": [
    {
      "candidates": [
        {
          "token": "string",
          "tokenId": "integer",
          "logProbability": "number"
        }
      ]
    }
  ],
  "chosenCandidates": [
    {
      "token": "string",
      "tokenId": "integer",
      "logProbability": "number"
    }
  ],
  "logProbabilitySum": "number"
}
UrlContextMetadata
code
JSON
download
content_copy
expand_less
{
  "urlMetadata": [
    {
      "retrievedUrl": "string",
      "urlRetrievalStatus": "URL_RETRIEVAL_STATUS_UNSPECIFIED | URL_RETRIEVAL_STATUS_SUCCESS | URL_RETRIEVAL_STATUS_ERROR | URL_RETRIEVAL_STATUS_PAYWALL | URL_RETRIEVAL_STATUS_UNSAFE"
    }
  ]
}
Sources
help
Generating content | Gemini API | Google AI for Developers