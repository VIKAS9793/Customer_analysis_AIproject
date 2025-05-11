/**
 * FinConnectAI Design System Integration
 * Version: 1.0.0
 * 
 * This script loads and integrates the FinConnectAI design system with existing templates.
 * It provides a non-invasive way to enhance the UI without modifying the original templates.
 * 
 * ETHICAL CONSIDERATIONS:
 * - Respects user preferences (reduced motion, dark mode, etc.)
 * - Enhances accessibility without disrupting existing functionality
 * - Provides ethical risk visualization
 * - All enhancements are applied progressively
 */

(function() {
  // Configuration
  const config = {
    // Paths to design system files
    paths: {
      css: [
        '/static/design-system/variables.css',
        '/static/design-system/components.css',
        '/static/design-system/utilities.css',
        '/static/design-system/theme-integration.css'
      ],
      js: [
        '/static/design-system/core.js',
        '/static/design-system/mock-data.js',
        '/static/design-system/ai-explanation.js',
        '/static/design-system/template-enhancer.js'
      ]
    },
    // Feature flags
    features: {
      darkMode: true,
      accessibilityEnhancements: true,
      interactiveComponents: true,
      mockData: true
    }
  };
  
  /**
   * Load a CSS file
   * @param {string} path - Path to CSS file
   * @returns {Promise} Promise that resolves when the CSS is loaded
   */
  function loadCSS(path) {
    return new Promise((resolve, reject) => {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = path;
      
      link.onload = () => resolve();
      link.onerror = () => {
        console.warn(`Failed to load CSS: ${path}`);
        resolve(); // Resolve anyway to continue loading other files
      };
      
      document.head.appendChild(link);
    });
  }
  
  /**
   * Load a JavaScript file
   * @param {string} path - Path to JavaScript file
   * @returns {Promise} Promise that resolves when the script is loaded
   */
  function loadScript(path) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = path;
      
      script.onload = () => resolve();
      script.onerror = () => {
        console.warn(`Failed to load script: ${path}`);
        resolve(); // Resolve anyway to continue loading other files
      };
      
      document.body.appendChild(script);
    });
  }
  
  /**
   * Initialize the design system integration
   */
  async function initialize() {
    console.log('Initializing FinConnectAI Design System Integration');
    
    try {
      // Load CSS files
      const cssPromises = config.paths.css.map(loadCSS);
      await Promise.all(cssPromises);
      console.log('Design system CSS loaded');
      
      // Load JavaScript files
      const jsPromises = config.paths.js.map(loadScript);
      await Promise.all(jsPromises);
      console.log('Design system JavaScript loaded');
      
      // Add integration complete class to body
      document.body.classList.add('fc-integration-complete');
      
      // Dispatch event to notify that integration is complete
      document.dispatchEvent(new CustomEvent('finconnect:integrated'));
      
    } catch (error) {
      console.error('Error initializing FinConnectAI Design System:', error);
    }
  }
  
  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }
})();
