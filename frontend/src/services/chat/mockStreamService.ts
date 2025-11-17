/**
 * Mock Stream Service
 *
 * Simulates Server-Sent Events (SSE) streaming for testing without backend.
 * Provides token-by-token streaming like a real LLM.
 */

import { StreamChunk } from '../../types/chat.types';

/**
 * Mock streaming function
 * Simulates SSE streaming by sending tokens one at a time
 */
export const mockStreamResponse = async (
  prompt: string,
  onToken: (content: string) => void,
  onComplete: (messageId: string) => void,
  onError: (error: string) => void,
  signal?: AbortSignal
): Promise<void> => {
  try {
    // Generate response based on prompt
    const response = getMockResponse(prompt);
    const messageId = `msg_${Date.now()}`;

    // Send start chunk
    console.log('🚀 Mock Stream: Starting...');

    // Split response into tokens (words and punctuation)
    const tokens = response.match(/\S+\s*|\s+/g) || [];

    // Stream tokens with realistic delays
    for (let i = 0; i < tokens.length; i++) {
      // Check if cancelled
      if (signal?.aborted) {
        console.log('⛔ Mock Stream: Cancelled by user');
        const abortError = new Error('Stream cancelled by user');
        abortError.name = 'AbortError';
        throw abortError;
      }

      const token = tokens[i];
      
      // Random delay between 30-100ms per token (simulates LLM generation)
      const delay = Math.random() * 70 + 30;
      await new Promise((resolve) => setTimeout(resolve, delay));

      // Check again after delay (for responsiveness)
      if (signal?.aborted) {
        console.log('⛔ Mock Stream: Cancelled by user');
        const abortError = new Error('Stream cancelled by user');
        abortError.name = 'AbortError';
        throw abortError;
      }

      // Send token
      onToken(token);

      // Occasional longer pause for punctuation
      if (token.includes('.') || token.includes('!') || token.includes('?')) {
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
    }

    // Send completion
    console.log('✅ Mock Stream: Complete');
    onComplete(messageId);
  } catch (error: any) {
    // Re-throw AbortError so it can be caught by useChatStream
    if (error.name === 'AbortError') {
      throw error;
    }
    // Handle other errors
    console.error('❌ Mock Stream: Error', error);
    onError(error instanceof Error ? error.message : 'Stream error');
    throw error;
  }
};

/**
 * Generate mock response based on prompt
 */
const getMockResponse = (prompt: string): string => {
  const lowerPrompt = prompt.toLowerCase();

  // TinyLlama-style responses with more natural conversational tone
  
  if (lowerPrompt.includes('hello') || lowerPrompt.includes('hi ') || lowerPrompt.includes('hey')) {
    return "Hello! I'm TinyLlama, a compact language model running right here on your device. How can I assist you today?";
  }

  if (lowerPrompt.includes('who are you') || lowerPrompt.includes('what are you')) {
    return "I'm TinyLlama, a 1.1 billion parameter language model. I'm designed to be small enough to run efficiently on consumer hardware while still being capable of helping with various tasks. Think of me as a lightweight AI assistant that respects your privacy by running locally!";
  }

  if (lowerPrompt.includes('tinyllama') || lowerPrompt.includes('tiny llama')) {
    return "TinyLlama is an open-source language model with 1.1B parameters, trained on approximately 3 trillion tokens. Despite being compact, it achieves impressive performance on many tasks. The model is based on the Llama 2 architecture and uses techniques like grouped-query attention to be efficient. It's perfect for running on local hardware!";
  }

  if (lowerPrompt.includes('how are you') || lowerPrompt.includes('how do you do')) {
    return "I'm functioning well, thank you for asking! As an AI model, I'm always ready to help. What would you like to know or discuss?";
  }

  if (lowerPrompt.includes('weather') || lowerPrompt.includes('temperature')) {
    return "I don't have access to real-time weather data since I'm running locally on your device without internet connectivity. However, I'd recommend checking a weather website or app for current conditions in your area!";
  }

  if (lowerPrompt.includes('write') && (lowerPrompt.includes('code') || lowerPrompt.includes('program'))) {
    return "I'd be happy to help with code! While I'm a smaller model, I can assist with basic programming tasks in languages like Python, JavaScript, and more. Please specify what kind of code you'd like me to write, and I'll do my best to help!";
  }

  if (lowerPrompt.includes('explain') && lowerPrompt.includes('ai')) {
    return "Artificial Intelligence (AI) is a field of computer science focused on creating systems that can perform tasks typically requiring human intelligence. This includes learning from data (machine learning), understanding language (NLP), recognizing patterns, and making decisions. AI systems range from simple rule-based programs to complex neural networks like myself!";
  }

  if (lowerPrompt.includes('machine learning') || lowerPrompt.includes('deep learning')) {
    return "Machine Learning is a subset of AI where systems learn patterns from data rather than following explicit instructions. Deep Learning, a specialized form of ML, uses artificial neural networks with multiple layers to learn hierarchical representations. These techniques power many modern AI applications, including language models like me!";
  }

  if (lowerPrompt.includes('python')) {
    return "Python is a versatile, high-level programming language known for its readability and simplicity. It's widely used in web development, data science, machine learning, automation, and more. Python's extensive library ecosystem (like NumPy, Pandas, PyTorch) makes it particularly popular for AI and scientific computing. Would you like to know about any specific Python topics?";
  }

  if (lowerPrompt.includes('javascript') || lowerPrompt.includes('js')) {
    return "JavaScript is the primary programming language for web development, running in browsers to create interactive websites. With Node.js, it can also run on servers. Modern JavaScript includes powerful features like async/await, destructuring, and arrow functions. Frameworks like React, Vue, and Angular build upon JavaScript to create rich user interfaces!";
  }

  if (lowerPrompt.includes('react')) {
    return "React is a popular JavaScript library for building user interfaces, created by Meta (Facebook). It uses a component-based architecture where UIs are broken into reusable pieces. React's virtual DOM makes updates efficient, and features like hooks make state management more intuitive. It's widely used for building modern web applications!";
  }

  if (lowerPrompt.includes('help') || lowerPrompt.includes('what can you do') || lowerPrompt.includes('capabilities')) {
    return "I can help you with various tasks:\n\n• Answering questions on diverse topics\n• Explaining concepts (science, technology, history, etc.)\n• Writing and editing text\n• Basic coding assistance\n• General conversation and brainstorming\n• Math and logic problems\n\nAs a smaller model running locally, I work best with clear, specific questions. What would you like to explore?";
  }

  if (lowerPrompt.includes('thank')) {
    return "You're welcome! I'm here to help. Feel free to ask if you have more questions!";
  }

  if (lowerPrompt.includes('bye') || lowerPrompt.includes('goodbye')) {
    return "Goodbye! It was nice chatting with you. Come back anytime you need help!";
  }

  // Generic intelligent response
  const topics = extractTopics(lowerPrompt);
  if (topics.length > 0) {
    return `That's an interesting question about ${topics.join(' and ')}! While I'm a compact model, I'll do my best to help. ${prompt.includes('?') ? "Let me break this down:" : "Here's what I can tell you:"} As TinyLlama, I aim to provide helpful responses based on my training. Could you provide more specific details about what aspect you'd like to explore?`;
  }

  // Fallback
  return `I understand you're asking about "${prompt}". As TinyLlama, I'm designed to be helpful while running efficiently on your device. While I may not have all the information you're looking for, I can try to assist or point you in the right direction. Could you rephrase your question or provide more context?`;
};

/**
 * Extract potential topics from prompt
 */
const extractTopics = (prompt: string): string[] => {
  const topics: string[] = [];
  
  const keywords = [
    'science', 'math', 'history', 'programming', 'technology', 
    'art', 'music', 'literature', 'philosophy', 'economics',
    'biology', 'physics', 'chemistry', 'computer', 'software'
  ];

  keywords.forEach((keyword) => {
    if (prompt.includes(keyword)) {
      topics.push(keyword);
    }
  });

  return topics;
};

