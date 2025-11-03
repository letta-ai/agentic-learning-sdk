/**
 * Interceptor Registry
 *
 * Auto-detection and registration of SDK interceptors.
 */

import type { IBaseInterceptor } from './base';

// Registry of all available interceptor classes
const interceptorClasses: Array<new () => IBaseInterceptor> = [];

// Store installed interceptor instances
const installedInterceptors: IBaseInterceptor[] = [];

/**
 * Register an interceptor class
 */
export function registerInterceptor(
  interceptorClass: new () => IBaseInterceptor
): void {
  if (!interceptorClasses.includes(interceptorClass)) {
    interceptorClasses.push(interceptorClass);
  }
}

/**
 * Auto-detect and install available SDK interceptors
 *
 * Checks each registered interceptor to see if its SDK is available,
 * and installs it if so.
 *
 * @returns List of installed interceptor provider names
 */
export function install(): string[] {
  const installed: string[] = [];

  if (process.env.DEBUG_AGENTIC_LEARNING) {
    console.log('[AgenticLearning] Installing interceptors...');
    console.log('[AgenticLearning] Registered interceptor classes:', interceptorClasses.length);
  }

  for (const InterceptorClass of interceptorClasses) {
    const interceptor = new InterceptorClass();

    if (process.env.DEBUG_AGENTIC_LEARNING) {
      console.log(`[AgenticLearning] Checking ${interceptor.PROVIDER}...`);
    }

    if (interceptor.isAvailable()) {
      try {
        interceptor.install();
        installedInterceptors.push(interceptor);
        installed.push(interceptor.PROVIDER);

        if (process.env.DEBUG_AGENTIC_LEARNING) {
          console.log(`[AgenticLearning] ✓ Installed ${interceptor.PROVIDER} interceptor`);
        }
      } catch (error) {
        // Silently skip interceptors that fail to install
        if (process.env.DEBUG_AGENTIC_LEARNING) {
          console.error(`[AgenticLearning] ✗ Failed to install ${interceptor.PROVIDER}:`, error);
        }
      }
    } else {
      if (process.env.DEBUG_AGENTIC_LEARNING) {
        console.log(`[AgenticLearning] ✗ ${interceptor.PROVIDER} SDK not available`);
      }
    }
  }

  if (process.env.DEBUG_AGENTIC_LEARNING) {
    console.log(`[AgenticLearning] Installed ${installed.length} interceptors:`, installed);
  }

  return installed;
}

/**
 * Uninstall all installed interceptors
 */
export function uninstallAll(): void {
  for (const interceptor of installedInterceptors) {
    try {
      interceptor.uninstall();
    } catch (error) {
      // Silently skip interceptors that fail to uninstall
    }
  }

  installedInterceptors.length = 0;
}
