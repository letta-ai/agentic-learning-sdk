/**
 * Utility functions for examples.
 *
 * Provides colored terminal output helpers.
 */

import type { Message } from '../typescript/src/client/messages/client';

// ANSI color codes for terminal output
const YELLOW = '\x1b[33m';
const PURPLE = '\x1b[35m';
const GREEN = '\x1b[32m';
const RED = '\x1b[31m';
const RESET = '\x1b[0m';

/**
 * Print user message with yellow 'User:' prefix.
 */
export function printU(message: string, end: string = '\n', flush: boolean = false): void {
  process.stdout.write(`${YELLOW}User:${RESET} ${message}${end}`);
  if (flush) {
    // In Node.js, stdout is typically line-buffered
  }
}

/**
 * Print assistant message with purple 'Assistant:' prefix.
 */
export function printA(message: string, end: string = '\n', flush: boolean = false): void {
  process.stdout.write(`${PURPLE}Assistant:${RESET} ${message}${end}`);
  if (flush) {
    // In Node.js, stdout is typically line-buffered
  }
}

/**
 * Print green success message.
 */
export function printG(message: string, end: string = '\n'): void {
  process.stdout.write(`${GREEN}${message}${RESET}${end}`);
}

/**
 * Print red message.
 */
export function printR(message: string, end: string = '\n'): void {
  process.stdout.write(`${RED}${message}${RESET}${end}`);
}

/**
 * Print messages with appropriate formatting.
 */
export function printMessages(messages: Message[]): void {
  console.log('[printMessages] messages:', messages);
  for (const message of messages) {
    if (message.message_type === 'user_message' && typeof message.content === 'string') {
      printU(message.content);
    } else if (message.message_type === 'assistant_message' && typeof message.content === 'string') {
      printA(message.content);
    } else if (message.message_type === 'reasoning_message' && message.reasoning) {
      printA(message.reasoning);
    }
  }
}


/**
 * Helper function to sleep
 */
export function sleep(s: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, s * 1000));
}
