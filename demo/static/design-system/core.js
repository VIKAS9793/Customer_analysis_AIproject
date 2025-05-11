/**
 * FinConnectAI Design System Core
 * Version: 1.0.0
 * 
 * This module initializes the FinConnectAI design system and provides core functionality.
 * It handles theme management, accessibility features, and ethical AI visualization.
 * 
 * SECURITY AND ETHICAL CONSIDERATIONS:
 * - No external API calls or dependencies
 * - All data is processed client-side
 * - Privacy-preserving design (no tracking or data collection)
 * - Accessibility features built-in
 */

class FinConnectCore {
  constructor(options = {}) {
    this.options = {
      useMockData: true,
      theme: 'light',
      accessibilityFeatures: true,
      ...options
    };
    
    // Initialize state
    this.state = {
      theme: this.options.theme,
      mockData: null,
      components: {},
      userPreferences: this.loadUserPreferences()
    };
    
    // Initialize mock data if enabled
    if (this.options.useMockData) {
      this.initializeMockData();
    }
    
    // Initialize theme
    this.initializeTheme();
    
    // Initialize accessibility features
    if (this.options.accessibilityFeatures) {
      this.initializeAccessibility();
    }
    
    // Save state on page unload
    window.addEventListener('beforeunload', () => {
      this.saveUserPreferences();
    });
    
    console.log('FinConnectAI Design System initialized');
  }
  
  /**
   * Initialize mock data for demonstrations
   */
  initializeMockData() {
    try {
      this.state.mockData = new FinConnectMockData();
      console.log('Mock data initialized with:', {
        transactions: this.state.mockData.transactions.length,
        users: this.state.mockData.users.length,
        alerts: this.state.mockData.alerts.length
      });
    } catch (error) {
      console.error('Failed to initialize mock data:', error);
    }
  }
  
  /**
   * Initialize theme based on user preference or system setting
   */
  initializeTheme() {
    // Check for saved preference
    const savedTheme = this.state.userPreferences.theme;
    
    if (savedTheme) {
      this.state.theme = savedTheme;
    } else {
      // Check for system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      this.state.theme = prefersDark ? 'dark' : 'light';
    }
    
    // Apply theme
    this.applyTheme(this.state.theme);
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
      if (!this.state.userPreferences.theme) {
        const newTheme = e.matches ? 'dark' : 'light';
        this.applyTheme(newTheme);
      }
    });
  }
  
  /**
   * Apply theme to document
   * @param {string} theme - Theme name ('light' or 'dark')
   */
  applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    this.state.theme = theme;
    
    // Store in preferences if user explicitly changed it
    if (this.state.userPreferences.themeExplicitlySet) {
      this.state.userPreferences.theme = theme;
    }
  }
  
  /**
   * Toggle between light and dark themes
   */
  toggleTheme() {
    const newTheme = this.state.theme === 'light' ? 'dark' : 'light';
    this.applyTheme(newTheme);
    
    // Mark as explicitly set by user
    this.state.userPreferences.themeExplicitlySet = true;
    this.state.userPreferences.theme = newTheme;
  }
  
  /**
   * Initialize accessibility features
   */
  initializeAccessibility() {
    // Add skip-to-content link
    this.addSkipToContentLink();
    
    // Ensure proper focus styles
    this.enforceFocusStyles();
    
    // Apply user accessibility preferences
    this.applyAccessibilityPreferences();
    
    // Listen for reduced motion preference
    window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', () => {
      this.applyAccessibilityPreferences();
    });
  }
  
  /**
   * Add skip-to-content link for keyboard users
   */
  addSkipToContentLink() {
    if (!document.getElementById('skip-to-content')) {
      const skipLink = document.createElement('a');
      skipLink.id = 'skip-to-content';
      skipLink.href = '#main-content';
      skipLink.className = 'fc-sr-only fc-focus-visible';
      skipLink.textContent = 'Skip to main content';
      
      skipLink.addEventListener('focus', () => {
        skipLink.style.position = 'fixed';
        skipLink.style.top = '0';
        skipLink.style.left = '0';
        skipLink.style.padding = '10px';
        skipLink.style.background = 'var(--finconnect-primary)';
        skipLink.style.color = 'white';
        skipLink.style.zIndex = '9999';
        skipLink.style.textDecoration = 'none';
      });
      
      skipLink.addEventListener('blur', () => {
        skipLink.style.position = 'absolute';
        skipLink.style.left = '-9999px';
      });
      
      document.body.insertBefore(skipLink, document.body.firstChild);
    }
    
    // Ensure main content has appropriate ID
    const mainContent = document.querySelector('main') || document.querySelector('.main-content');
    if (mainContent && !mainContent.id) {
      mainContent.id = 'main-content';
    }
  }
  
  /**
   * Ensure proper focus styles are applied
   */
  enforceFocusStyles() {
    // Add a class to the body when using keyboard navigation
    document.body.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        document.body.classList.add('keyboard-navigation');
      }
    });
    
    document.body.addEventListener('mousedown', () => {
      document.body.classList.remove('keyboard-navigation');
    });
    
    // Add global styles for focus if not already present
    if (!document.getElementById('fc-focus-styles')) {
      const style = document.createElement('style');
      style.id = 'fc-focus-styles';
      style.textContent = `
        body.keyboard-navigation *:focus {
          outline: 2px solid var(--finconnect-primary) !important;
          outline-offset: 2px !important;
        }
      `;
      document.head.appendChild(style);
    }
  }
  
  /**
   * Apply user accessibility preferences
   */
  applyAccessibilityPreferences() {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const userPrefersReducedMotion = this.state.userPreferences.reducedMotion;
    
    // Apply reduced motion if either system or user preference indicates it
    if (prefersReducedMotion || userPrefersReducedMotion) {
      document.documentElement.classList.add('reduced-motion');
    } else {
      document.documentElement.classList.remove('reduced-motion');
    }
    
    // Apply high contrast if user prefers it
    if (this.state.userPreferences.highContrast) {
      document.documentElement.classList.add('high-contrast');
    } else {
      document.documentElement.classList.remove('high-contrast');
    }
    
    // Apply font size adjustment
    if (this.state.userPreferences.fontSize) {
      document.documentElement.style.fontSize = `${this.state.userPreferences.fontSize}%`;
    } else {
      document.documentElement.style.fontSize = '';
    }
  }
  
  /**
   * Set accessibility preference
   * @param {string} preference - Preference name
   * @param {any} value - Preference value
   */
  setAccessibilityPreference(preference, value) {
    this.state.userPreferences[preference] = value;
    this.applyAccessibilityPreferences();
  }
  
  /**
   * Load user preferences from localStorage
   * @returns {Object} User preferences
   */
  loadUserPreferences() {
    try {
      const savedPreferences = localStorage.getItem('finconnectai.preferences');
      return savedPreferences ? JSON.parse(savedPreferences) : {
        theme: null,
        themeExplicitlySet: false,
        reducedMotion: false,
        highContrast: false,
        fontSize: 100,
        dashboardLayout: null
      };
    } catch (error) {
      console.error('Failed to load user preferences:', error);
      return {
        theme: null,
        themeExplicitlySet: false,
        reducedMotion: false,
        highContrast: false,
        fontSize: 100,
        dashboardLayout: null
      };
    }
  }
  
  /**
   * Save user preferences to localStorage
   */
  saveUserPreferences() {
    try {
      localStorage.setItem('finconnectai.preferences', JSON.stringify(this.state.userPreferences));
    } catch (error) {
      console.error('Failed to save user preferences:', error);
    }
  }
  
  /**
   * Register a component with the core system
   * @param {string} name - Component name
   * @param {Object} component - Component instance
   */
  registerComponent(name, component) {
    this.state.components[name] = component;
  }
  
  /**
   * Get a registered component
   * @param {string} name - Component name
   * @returns {Object} Component instance
   */
  getComponent(name) {
    return this.state.components[name];
  }
  
  /**
   * Format a date for display
   * @param {Date} date - Date to format
   * @param {string} format - Format type ('short', 'medium', 'long')
   * @returns {string} Formatted date string
   */
  formatDate(date, format = 'medium') {
    if (!date) return '';
    
    try {
      const dateObj = date instanceof Date ? date : new Date(date);
      
      switch (format) {
        case 'short':
          return dateObj.toLocaleDateString();
        case 'long':
          return dateObj.toLocaleDateString(undefined, { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          });
        case 'time':
          return dateObj.toLocaleTimeString(undefined, { 
            hour: '2-digit', 
            minute: '2-digit' 
          });
        case 'datetime':
          return `${dateObj.toLocaleDateString()} ${dateObj.toLocaleTimeString(undefined, { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}`;
        case 'medium':
        default:
          return dateObj.toLocaleDateString(undefined, { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
          });
      }
    } catch (error) {
      console.error('Date formatting error:', error);
      return String(date);
    }
  }
  
  /**
   * Format a currency value for display
   * @param {number} amount - Amount to format
   * @param {string} currency - Currency code (e.g., 'USD')
   * @returns {string} Formatted currency string
   */
  formatCurrency(amount, currency = 'USD') {
    if (amount === undefined || amount === null) return '';
    
    try {
      return new Intl.NumberFormat(undefined, {
        style: 'currency',
        currency: currency
      }).format(amount);
    } catch (error) {
      console.error('Currency formatting error:', error);
      return `${currency} ${amount.toFixed(2)}`;
    }
  }
  
  /**
   * Format a percentage for display
   * @param {number} value - Value to format as percentage
   * @param {number} decimals - Number of decimal places
   * @returns {string} Formatted percentage string
   */
  formatPercentage(value, decimals = 1) {
    if (value === undefined || value === null) return '';
    
    try {
      return new Intl.NumberFormat(undefined, {
        style: 'percent',
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
      }).format(value);
    } catch (error) {
      console.error('Percentage formatting error:', error);
      return `${(value * 100).toFixed(decimals)}%`;
    }
  }
  
  /**
   * Get risk level class based on risk score
   * @param {number} score - Risk score (0-1)
   * @returns {string} Risk level class name
   */
  getRiskLevelClass(score) {
    if (score === undefined || score === null) return 'unknown-risk';
    
    if (score < 0.3) {
      return 'low-risk';
    } else if (score < 0.7) {
      return 'medium-risk';
    } else {
      return 'high-risk';
    }
  }
  
  /**
   * Get risk level label based on risk score
   * @param {number} score - Risk score (0-1)
   * @returns {string} Risk level label
   */
  getRiskLevelLabel(score) {
    if (score === undefined || score === null) return 'Unknown';
    
    if (score < 0.3) {
      return 'Low';
    } else if (score < 0.7) {
      return 'Medium';
    } else {
      return 'High';
    }
  }
  
  /**
   * Create an element with attributes and content
   * @param {string} tag - HTML tag name
   * @param {Object} attributes - Element attributes
   * @param {string|Node|Array} content - Element content
   * @returns {HTMLElement} Created element
   */
  createElement(tag, attributes = {}, content = null) {
    const element = document.createElement(tag);
    
    // Set attributes
    Object.entries(attributes).forEach(([key, value]) => {
      if (key === 'className') {
        element.className = value;
      } else if (key === 'dataset') {
        Object.entries(value).forEach(([dataKey, dataValue]) => {
          element.dataset[dataKey] = dataValue;
        });
      } else if (key.startsWith('on') && typeof value === 'function') {
        element.addEventListener(key.substring(2).toLowerCase(), value);
      } else {
        element.setAttribute(key, value);
      }
    });
    
    // Add content
    if (content !== null) {
      if (Array.isArray(content)) {
        content.forEach(item => {
          if (item instanceof Node) {
            element.appendChild(item);
          } else {
            element.appendChild(document.createTextNode(String(item)));
          }
        });
      } else if (content instanceof Node) {
        element.appendChild(content);
      } else {
        element.textContent = String(content);
      }
    }
    
    return element;
  }
}

// Initialize global instance when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.FinConnect = new FinConnectCore();
});
