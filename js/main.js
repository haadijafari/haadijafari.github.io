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
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const scrollto = (el) => {
      const target = select(el);
      const behavior = reduceMotion ? "instant" : "smooth";
      // data-scroll="center" puts the target mid-screen (the Contact block)
      if (target.dataset.scroll === "center") {
        target.scrollIntoView({ block: "center", behavior });
      } else {
        window.scrollTo({ top: target.offsetTop, behavior });
      }
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
    const setMobileNav = (open) => {
      const toggle = select(".mobile-nav-toggle");
      select("body").classList.toggle("mobile-nav-active", open);
      toggle.setAttribute("aria-expanded", open);
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      toggle.querySelector("use").setAttribute("href", open ? "#i-x-lg" : "#i-list");
    };
    on("click", ".mobile-nav-toggle", function (e) {
      setMobileNav(!select("body").classList.contains("mobile-nav-active"));
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && select("body").classList.contains("mobile-nav-active")) {
        setMobileNav(false);
        select(".mobile-nav-toggle").focus();
      }
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
  
          if (select("body").classList.contains("mobile-nav-active")) {
            setMobileNav(false);
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
     * Hero type effect (a static first role when motion is reduced)
     */
    const typed = select(".typed");
    if (typed && !reduceMotion) {
      let typed_strings = typed.getAttribute("data-typed-items");
      typed_strings = typed_strings.split(",").map((s) => s.trim());
      new Typed(".typed", {
        strings: typed_strings,
        loop: true,
        typeSpeed: 70,
        backSpeed: 35,
        backDelay: 2000,
      });
    }
  
    /**
     * Hobbies deck: a shuffled polaroid stack on phones, a spread row on wider screens
     */
    const initDeck = (root) => {
      const cards = [...root.querySelectorAll(".polaroid")];
      const text = root.closest("section").querySelector(".deck-text");
      const tilts = [-4, 5, -8, 7, -2];
      const wide = window.matchMedia("(min-width: 768px)");
      let order = cards.map((_, i) => i);

      const showText = (card) => {
        text.textContent = card.dataset.text;
      };
      const layoutStack = () => {
        order.forEach((idx, depth) => {
          const card = cards[idx];
          card.style.zIndex = cards.length - depth;
          card.style.setProperty("--depth", depth);
          card.style.setProperty("--tilt", (depth === 0 ? -2 : tilts[idx]) + "deg");
        });
        showText(cards[order[0]]);
      };
      const layout = () => {
        if (wide.matches) {
          cards.forEach((card, i) => {
            card.style.zIndex = "";
            card.style.setProperty("--tilt", tilts[i] + "deg");
            card.tabIndex = 0;
          });
          showText(cards[0]);
        } else {
          cards.forEach((card) => card.removeAttribute("tabindex"));
          layoutStack();
        }
      };

      root.querySelector(".deck-shuffle").addEventListener("click", () => {
        order.push(order.shift());
        layoutStack();
      });
      cards.forEach((card) => {
        card.addEventListener("mouseenter", () => wide.matches && showText(card));
        card.addEventListener("focus", () => showText(card));
      });
      wide.addEventListener("change", layout);
      layout();
    };
    select("[data-deck]", true).forEach(initDeck);

    /**
     * Projects: a swipeable card deck on phones, a contents list and fanned cards on wide screens.
     * The counter, dots and list are built from the cards, so adding a project only needs a new card.
     */
    const initProjects = (root) => {
      const stage = root.querySelector(".project-stage");
      const cards = [...stage.querySelectorAll(".project-card")];
      const n = cards.length;
      if (n < 2) return;
      const index = root.querySelector(".project-index");
      const nav = root.querySelector(".project-nav");
      const dots = root.querySelector(".project-dots");
      const status = root.querySelector(".project-status");
      const wide = window.matchMedia("(min-width: 992px)");
      let cur = 0;
      let busy = false;

      cards.forEach((card, i) => {
        const count = document.createElement("span");
        count.className = "project-count";
        count.setAttribute("aria-hidden", "true");
        count.textContent = `${i + 1}/${n}`;
        card.prepend(count);
        card.setAttribute("role", "group");
        card.setAttribute("aria-roledescription", "slide");
        card.setAttribute("aria-label", `${i + 1} of ${n}`);

        const li = document.createElement("li");
        li.innerHTML = '<button type="button"><span class="index-num"></span><span class="index-title"></span><span class="index-cat"></span></button>';
        li.querySelector(".index-num").textContent = String(i + 1).padStart(2, "0");
        li.querySelector(".index-title").textContent = card.querySelector("h3").textContent;
        li.querySelector(".index-cat").textContent = card.querySelector(".project-cat").textContent;
        li.querySelector("button").addEventListener("click", () => show(i));
        index.append(li);

        dots.append(document.createElement("i"));
      });
      const indexButtons = [...index.querySelectorAll("button")];
      const dotEls = [...dots.children];

      const render = () => {
        cards.forEach((card, i) => {
          const pos = (i - cur + n) % n; // depth in the deck
          const rel = pos > n / 2 ? pos - n : pos; // place in the fan: -1 left, 0 front, 1 right
          const current = i === cur;
          card.style.setProperty("--pos", pos);
          card.style.setProperty("--rel", rel);
          card.style.setProperty("--abs", Math.abs(rel));
          card.style.zIndex = n - (wide.matches ? Math.abs(rel) : pos);
          card.classList.toggle("is-current", current);
          card.classList.toggle("is-far", Math.abs(rel) > 1);
          card.setAttribute("aria-hidden", !current);
          card.querySelectorAll("a").forEach((a) => (a.tabIndex = current ? 0 : -1));
        });
        indexButtons.forEach((b, i) => b.setAttribute("aria-current", i === cur));
        dotEls.forEach((d, i) => d.classList.toggle("on", i === cur));
      };
      const announce = () => {
        status.textContent = `Project ${cur + 1} of ${n}: ${cards[cur].querySelector("h3").textContent}`;
      };

      // jump straight to a card (fan, list, reduced motion)
      const show = (i) => {
        if (busy || i === cur) return;
        cur = (i + n) % n;
        render();
        announce();
      };
      // next: on the deck the top card flies off before the next one rises
      const next = (dir = -1) => {
        if (wide.matches || reduceMotion) return show(cur + 1);
        if (busy) return;
        busy = true;
        const top = cards[cur];
        top.style.setProperty("--fling", dir);
        top.classList.add("is-flung");
        setTimeout(() => {
          top.classList.remove("is-flung");
          busy = false;
          show(cur + 1);
        }, 260);
      };
      // previous: on the deck the last card flies back in from the left
      const prev = () => {
        if (wide.matches || reduceMotion) return show(cur - 1);
        if (busy) return;
        const card = cards[(cur - 1 + n) % n];
        card.style.transition = "none";
        card.style.setProperty("--fling", -1);
        card.classList.add("is-flung");
        card.style.zIndex = n + 1;
        void card.offsetWidth;
        card.style.transition = "";
        card.classList.remove("is-flung");
        show(cur - 1);
      };

      root.querySelector(".project-next").addEventListener("click", () => next());
      root.querySelector(".project-prev").addEventListener("click", prev);
      root.addEventListener("keydown", (e) => {
        if (e.key === "ArrowRight") next();
        else if (e.key === "ArrowLeft") prev();
        else return;
        e.preventDefault();
      });

      // a side card in the fan comes to the front instead of following its link
      stage.addEventListener("click", (e) => {
        const card = e.target.closest(".project-card");
        if (dragged || (card && card !== cards[cur])) {
          e.preventDefault();
          if (!dragged && card) show(cards.indexOf(card));
        }
      });

      // swipe: on the deck the card follows the finger; any direction sends it to the back
      let startX = null;
      let dx = 0;
      let dragged = false;
      stage.addEventListener("pointerdown", (e) => {
        if (e.button !== 0 || busy || !e.target.closest(".is-current")) return;
        startX = e.clientX;
        dx = 0;
        dragged = false;
      });
      stage.addEventListener("pointermove", (e) => {
        if (startX === null) return;
        dx = e.clientX - startX;
        const top = cards[cur];
        if (!dragged && Math.abs(dx) > 8) {
          dragged = true;
          stage.setPointerCapture(e.pointerId);
          top.classList.add("is-dragging");
        }
        if (dragged && !wide.matches) {
          top.style.transform = `translateX(${dx}px) rotate(${dx / 20}deg)`;
        }
      });
      const endDrag = () => {
        if (startX === null) return;
        startX = null;
        if (!dragged) return;
        const top = cards[cur];
        top.classList.remove("is-dragging");
        top.style.transform = "";
        if (Math.abs(dx) > 60) {
          if (wide.matches) dx < 0 ? show(cur + 1) : show(cur - 1);
          else next(dx > 0 ? 1 : -1);
        }
        // swallow the click that follows the drag
        setTimeout(() => (dragged = false));
      };
      stage.addEventListener("pointerup", endDrag);
      stage.addEventListener("pointercancel", endDrag);

      index.hidden = false;
      nav.hidden = false;
      // the first layout appears in place instead of animating out of a flat pile
      cards.forEach((card) => (card.style.transition = "none"));
      root.classList.add("is-ready");
      render();
      void stage.offsetWidth;
      cards.forEach((card) => (card.style.transition = ""));
      wide.addEventListener("change", render);
    };
    select("[data-projects]", true).forEach(initProjects);

    /**
     * Certifications: dots under the highlight row on phones (it scrolls natively with snap).
     * The dots are built from the cards and hidden by CSS once the row turns into a grid.
     */
    const initCertRail = (root) => {
      const rail = root.querySelector(".cert-rail");
      const cards = [...rail.querySelectorAll(".cert-card")];
      const dots = root.querySelector(".cert-dots");
      if (cards.length < 2) return;

      const buttons = cards.map((card, i) => {
        const b = document.createElement("button");
        b.type = "button";
        b.setAttribute("aria-label", `Show ${card.querySelector("h3").textContent}`);
        b.addEventListener("click", () => rail.scrollTo({ left: cards[i].offsetLeft - cards[0].offsetLeft }));
        dots.append(b);
        return b;
      });

      const update = () => {
        const step = cards[1].offsetLeft - cards[0].offsetLeft;
        const atEnd = rail.scrollLeft >= rail.scrollWidth - rail.clientWidth - 2;
        const cur = atEnd ? cards.length - 1 : Math.round(rail.scrollLeft / step);
        buttons.forEach((b, i) => b.setAttribute("aria-current", i === cur));
      };
      rail.addEventListener("scroll", update, { passive: true });
      dots.hidden = false;
      update();
    };
    select("[data-cert-rail]", true).forEach(initCertRail);

    /**
     * About intro: collapsed on phones, Read more / Show less
     */
    const intro = select("#about-intro");
    const introToggle = select(".intro-toggle");
    if (intro && introToggle) {
      const wide = window.matchMedia("(min-width: 992px)");
      const setOpen = (open) => {
        intro.classList.toggle("is-collapsed", !open);
        introToggle.setAttribute("aria-expanded", open);
        introToggle.textContent = open ? "Show less" : "Read more";
      };
      introToggle.hidden = false;
      setOpen(false);
      introToggle.addEventListener("click", () => setOpen(intro.classList.contains("is-collapsed")));
      // tapping the faded text opens it; closing goes through the button
      intro.addEventListener("click", () => {
        if (!wide.matches && intro.classList.contains("is-collapsed")) setOpen(true);
      });
    }
  
    /**
     * GLightbox
     */
    const lightbox = GLightbox({
      selector: ".certifications-lightbox",
      openEffect: "fade",
      loop: true,
      closeButton: true,
      moreLength: 0,
    });
  })();

// Age (birthday April 2003) and certificate count
document.addEventListener("DOMContentLoaded", function () {
  // month is 0-based: 3 = April
  function ageFrom(year, month) {
    var now = new Date();
    return now.getFullYear() - year - (now.getMonth() < month ? 1 : 0);
  }
  document.getElementById("age").textContent = ageFrom(2003, 3);
  document.getElementById("year").textContent = new Date().getFullYear();

  // Counts the certificates (cards and list rows), so adding one updates the number.
  // Keeps the HTML fallback if no cards are found.
  function countCertificates() {
    return document.querySelectorAll("#certifications .certifications-lightbox").length;
  }
  var count = countCertificates();
  if (count > 0) {
    document.getElementById("cert-count").textContent = count;
  }
});
