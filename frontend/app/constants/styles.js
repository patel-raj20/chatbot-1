/**
 * Style Constants
 * ===============
 * Reusable Tailwind CSS class combinations
 */

export const GRADIENTS = {
  primary: 'bg-gradient-to-br from-violet-600 via-purple-600 to-indigo-700',
  header: 'bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600',
  button: 'bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600',
  userMessage: 'bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-600',
  messagesBg: 'bg-gradient-to-b from-slate-50 to-purple-50',
  admin: 'bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900',
};

export const BUTTON_STYLES = {
  primary: 'px-4 py-2 bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600 text-white rounded-lg font-semibold hover:shadow-xl transform hover:scale-105 transition-all',
  secondary: 'px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg font-medium transition-all backdrop-blur-sm border border-white/30',
  danger: 'px-4 py-2 bg-red-500/80 hover:bg-red-600 text-white rounded-lg font-medium transition-all backdrop-blur-sm border border-white/30',
  success: 'px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition-colors',
  option: 'relative group overflow-hidden bg-gradient-to-r from-violet-500 via-purple-500 to-fuchsia-500 text-white px-5 py-2.5 rounded-full text-sm font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 hover:-translate-y-0.5',
};

export const ANIMATIONS = {
  slideInLeft: 'animate-slide-in-left',
  slideInRight: 'animate-slide-in-right',
  fadeIn: 'animate-fade-in',
};

export const KEYFRAMES = `
@keyframes slide-in-left {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
@keyframes slide-in-right {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
@keyframes fade-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
.animate-slide-in-left {
  animation: slide-in-left 0.4s ease-out;
}
.animate-slide-in-right {
  animation: slide-in-right 0.4s ease-out;
}
.animate-fade-in {
  animation: fade-in 0.5s ease-out;
}
`;
