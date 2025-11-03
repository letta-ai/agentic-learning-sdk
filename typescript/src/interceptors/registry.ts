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

  for (const InterceptorClass of interceptorClasses) {
    const interceptor = new InterceptorClass();

    if (interceptor.isAvailable()) {
      try {
        interceptor.install();
        installedInterceptors.push(interceptor);
        installed.push(interceptor.PROVIDER);
      } catch (error) {
        // Silently skip interceptors that fail to install
      }
    }
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
