/**
 * Style Constants
 * ===============
 * Professional Enterprise Color Scheme
 */

// Professional Color Palette
export const COLORS = {
  // Primary Color - Indigo Blue
  primary: '#4F6BED',
  primaryHover: '#3D56D9',
  primaryLight: '#EEF2FF',
  
  // Secondary Accent - Soft Teal
  secondary: '#2CB1A6',
  secondaryHover: '#239B91',
  secondaryLight: '#E6F7F5',
  
  // Background Colors
  appBg: '#F5F7FA',
  cardBg: '#FFFFFF',
  
  // Text Colors
  textPrimary: '#1F2937',
  textSecondary: '#6B7280',
  textMuted: '#9CA3AF',
  
  // Chat Bubble Colors
  botBubbleBg: '#EEF2FF',
  botBubbleText: '#1F2937',
  userBubbleBg: '#E6F7F5',
  userBubbleText: '#0F3D3A',
  
  // Danger/Logout
  danger: '#E5533D',
  dangerHover: '#CC3F2B',
  
  // Borders & Dividers
  border: '#E5E7EB',
  
  // Status
  online: '#2CB1A6',
};

export const GRADIENTS = {
  primary: 'bg-[#F5F7FA]',
  header: 'bg-[#4F6BED]',
  messagesBg: 'bg-[#F5F7FA]',
  admin: 'bg-[#4F6BED]',
};

export const BUTTON_STYLES = {
  primary: 'px-4 py-2 bg-[#4F6BED] hover:bg-[#3D56D9] text-white rounded-xl font-semibold shadow-md hover:shadow-lg transition-all duration-200',
  secondary: 'px-4 py-2 bg-white/90 hover:bg-white text-[#4F6BED] rounded-xl font-medium transition-all duration-200 border border-white/50 shadow-sm',
  danger: 'px-4 py-2 bg-[#E5533D] hover:bg-[#CC3F2B] text-white rounded-xl font-medium transition-all duration-200 shadow-md',
  success: 'px-4 py-2 bg-[#2CB1A6] hover:bg-[#239B91] text-white rounded-xl font-semibold transition-all duration-200 shadow-md',
  option: 'bg-[#4F6BED] hover:bg-[#3D56D9] text-white px-5 py-2.5 rounded-xl text-sm font-semibold shadow-md hover:shadow-lg transition-all duration-200',
  ghost: 'px-4 py-2 bg-transparent hover:bg-gray-100 text-[#6B7280] rounded-xl font-medium transition-all duration-200',
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
