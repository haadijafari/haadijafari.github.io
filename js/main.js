(function () {
    "use strict";
  
    /**
     * Easy selector helper function
     */
    const select = (el, all = false) => {
      el = el.trim();
      if (all) {
        return [...document.querySelectorAll(el)];
      } else {
        return document.querySelector(el);
      }
    };
  
    /**
     * Easy event listener function
     */
    const on = (type, el, listener, all = false) => {
      let selectEl = select(el, all);
      if (selectEl) {
        if (all) {
          selectEl.forEach((e) => e.addEventListener(type, listener));
        } else {
          selectEl.addEventListener(type, listener);
        }
      }
    };
  
    /**
     * Easy on scroll event listener
     */
    const onscroll = (el, listener) => {
      el.addEventListener("scroll", listener);
    };
  
    /**
     * Navbar links active state on scroll
     */
    let navbarlinks = select("#navbar .scrollto", true);
    const navbarlinksActive = () => {
      let position = window.scrollY + 200;
      navbarlinks.forEach((navbarlink) => {
        if (!navbarlink.hash) return;
        let section = select(navbarlink.hash);
        if (!section) return;
        if (
          position >= section.offsetTop &&
          position <= section.offsetTop + section.offsetHeight
        ) {
          navbarlink.classList.add("active");
        } else {
          navbarlink.classList.remove("active");
        }
      });
    };
    window.addEventListener("load", navbarlinksActive);
    onscroll(document, navbarlinksActive);
  
    /**
     * Scrolls to an element with header offset
     */
    const scrollto = (el) => {
      let elementPos = select(el).offsetTop;
      window.scrollTo({
        top: elementPos,
        behavior: "smooth",
      });
    };
  
    /**
     * Back to top button
     */
    let backtotop = select(".back-to-top");
    if (backtotop) {
      const toggleBacktotop = () => {
        if (window.scrollY > 100) {
          backtotop.classList.add("active");
        } else {
          backtotop.classList.remove("active");
        }
      };
      window.addEventListener("load", toggleBacktotop);
      onscroll(document, toggleBacktotop);
    }
  
    /**
     * Mobile nav toggle
     */
    on("click", ".mobile-nav-toggle", function (e) {
      select("body").classList.toggle("mobile-nav-active");
      this.classList.toggle("bi-list");
      this.classList.toggle("bi-x");
    });
  
    /**
     * Scrool with offset on links with a class name .scrollto
     */
    on(
      "click",
      ".scrollto",
      function (e) {
        if (select(this.hash)) {
          e.preventDefault();
  
          let body = select("body");
          if (body.classList.contains("mobile-nav-active")) {
            body.classList.remove("mobile-nav-active");
            let navbarToggle = select(".mobile-nav-toggle");
            navbarToggle.classList.toggle("bi-list");
            navbarToggle.classList.toggle("bi-x");
          }
          scrollto(this.hash);
        }
      },
      true
    );
  
    /**
     * Scroll with offset on page load with hash links in the url
     */
    window.addEventListener("load", () => {
      if (window.location.hash) {
        if (select(window.location.hash)) {
          scrollto(window.location.hash);
        }
      }
    });
  
    /**
     * Preloader
     */
    let preloader = select("#preloader");
    if (preloader) {
      window.addEventListener("load", () => {
        preloader.remove();
      });
    }
  
    /**
     * Hero type effect
     */
    const typed = select(".typed");
    if (typed) {
      let typed_strings = typed.getAttribute("data-typed-items");
      typed_strings = typed_strings.split(",");
      new Typed(".typed", {
        strings: typed_strings,
        loop: true,
        typeSpeed: 100,
        backSpeed: 50,
        backDelay: 2000,
      });
    }
  
    /**
     * counter effect
     */
    new PureCounter();
  
    // Or you can customize it for override the default config.
    // Here is the default configuration for all element with class 'filesizecount'
    new PureCounter({
      // Setting that can't' be overriden on pre-element
      selector: ".purecounter", // HTML query selector for spesific element
  
      // Settings that can be overridden on per-element basis, by `data-purecounter-*` attributes:
      start: 0, // Starting number [uint]
      end: 100, // End number [uint]
      duration: 2, // The time in seconds for the animation to complete [seconds]
      delay: 10, // The delay between each iteration (the default of 10 will produce 100 fps) [miliseconds]
      once: true, // Counting at once or recount when the element in view [boolean]
      pulse: false, // Repeat count for certain time [boolean:false|seconds]
      decimals: 0, // How many decimal places to show. [uint]
      legacy: true, // If this is true it will use the scroll event listener on browsers
      filesizing: false, // This will enable/disable File Size format [boolean]
      currency: false, // This will enable/disable Currency format. Use it for set the symbol too [boolean|char|string]
      formater: "us-US", // Number toLocaleString locale/formater, by default is "en-US" [string|boolean:false]
      separator: false, // This will enable/disable comma separator for thousands. Use it for set the symbol too [boolean|char|string]
    });
  
    /**
     * Porfolio isotope and filter
     */
    window.addEventListener("load", () => {
      let portfolioContainer = select(".portfolio-container");
      if (portfolioContainer) {
        let portfolioIsotope = new Isotope(portfolioContainer, {
          itemSelector: ".portfolio-item",
        });
  
        let portfolioFilters = select("#portfolio-flters li", true);
  
        on(
          "click",
          "#portfolio-flters li",
          function (e) {
            e.preventDefault();
            portfolioFilters.forEach(function (el) {
              el.classList.remove("filter-active");
            });
            this.classList.add("filter-active");
  
            portfolioIsotope.arrange({
              filter: this.getAttribute("data-filter"),
            });
            // portfolioIsotope.on("arrangeComplete", function () {
            //   AOS.refresh();
            // });
          },
          true
        );
      }
    });
  
    /**
     * Initiate portfolio lightbox
     */
    const portfolioLightbox = GLightbox({
      selector: ".portfolio-lightbox",
      openEffect: "zoom",
      openEffect: "fade",
      loop: true,
      closeButton: true,
      moreLength: 0,
    });
  
    /**
     * Initiate portfolio details lightbox
     */
    const portfolioDetailsLightbox = GLightbox({
      selector: ".portfolio-details-lightbox",
      width: "90%",
      height: "90vh",
    });
  
    /**
     * Skills animation
     */
    let skilsContent = select(".skills-content");
    if (skilsContent) {
      new Waypoint({
        element: skilsContent,
        offset: "80%",
        handler: function (direction) {
          let progress = select(".progress .progress-bar", true);
          progress.forEach((el) => {
            el.style.width = el.getAttribute("aria-valuenow") + "%";
          });
        },
      });
    }
  
    /**
     * GLightbox
     */
    const lightbox = GLightbox({
      selector: ".certifications-lightbox",
      openEffect: "zoom",
      openEffect: "fade",
      loop: true,
      closeButton: true,
      moreLength: 0,
    });
  })();

// Age calculator
document.addEventListener("DOMContentLoaded", function() {
    var currentYear = new Date().getFullYear();
    var birthYear = 2003;
    var age = currentYear - birthYear;
    document.getElementById("age").textContent = age;
  });
