import { toast } from 'sonner';

/**
 * Toast notification helper
 * Wrapper around Sonner for consistent notifications
 */
export const useToast = () => {
  const success = (message, options = {}) => {
    toast.success(message, {
      duration: 4000,
      ...options,
    });
  };

  const error = (message, options = {}) => {
    toast.error(message, {
      duration: 4000,
      ...options,
    });
  };

  const loading = (message, options = {}) => {
    return toast.loading(message, {
      ...options,
    });
  };

  const promise = (promise, messages, options = {}) => {
    return toast.promise(promise, messages, {
      duration: 4000,
      ...options,
    });
  };

  const info = (message, options = {}) => {
    toast.info(message, {
      duration: 4000,
      ...options,
    });
  };

  const dismiss = (toastId) => {
    toast.dismiss(toastId);
  };

  return {
    success,
    error,
    loading,
    promise,
    info,
    dismiss,
  };
};

export default useToast;
