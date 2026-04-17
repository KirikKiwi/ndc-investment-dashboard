/* v1776405322 */
/* ============================================================
   NDC Investment Dashboard
   globe.js — D3 globe with choropleth colouring
   ============================================================ */

(function() {

    const CONFIG = {
        autoRotateSpeed : 0.15,
        rotateDelay     : 3000,
        sensitivity     : 0.5,
        zoomMin         : 0.8,
        zoomMax         : 8.0,
        colours: {
            tier3    : "#c0392b",
            tier2    : "#e67e22",
            tier1    : "#00c896",
            noData   : "#1a1a1a",
            selected : "#00c896",
            hover    : "#ffffff",
            ocean    : "#050505",
            graticule: "#1a1a1a",
            border   : "#000000",
        }
    };

    let state = {
        rotating      : true,
        rotateTimer   : null,
        selectedISO   : null,
        countryData   : {},
        projection    : null,
        path          : null,
        svg           : null,
        countries     : null,
        scale         : 1,
        lastColourMode: null,
    };

    // Display names for territories not in NDC database
    const TERRITORY_NAMES = {
        "GRL": "Greenland",
        "ATA": "Antarctica",
        "ESH": "Western Sahara",
        "PRI": "Puerto Rico",
        "FLK": "Falkland Islands",
        "ATF": "French Southern Territories",
        "NCL": "New Caledonia",
        "TWN": "Taiwan",
    };

    function getDisplayName(iso, countryData) {
        if (countryData[iso] && countryData[iso].display_name) {
            return countryData[iso].display_name;
        }
        if (TERRITORY_NAMES[iso]) {
            return TERRITORY_NAMES[iso];
        }
        return iso || "Unknown region";
    }

    function getTierColour(iso) {
        const d = state.countryData[iso];
        if (!d) return CONFIG.colours.noData;
        const tier = d.investment_tier || "";
        if (tier.includes("Tier 1")) return CONFIG.colours.tier1;
        if (tier.includes("Tier 2")) return CONFIG.colours.tier2;
        if (tier.includes("Tier 3")) return CONFIG.colours.tier3;
        return CONFIG.colours.noData;
    }

    function showTooltip(event, iso, name) {
        const d  = state.countryData[iso] || {};
        const tt = document.getElementById("globe-tooltip");
        if (!tt) return;
        const tier      = d.investment_tier || "No data";
        const ndgain    = d.ndgain_score
                          ? parseFloat(d.ndgain_score).toFixed(1)
                          : "N/A";
        const renewable = d.renewable_electricity_pct
                          ? parseFloat(d.renewable_electricity_pct).toFixed(0) + "%"
                          : "N/A";
        tt.innerHTML = `
            <div style="font-weight:600;margin-bottom:4px;color:#f0f0f0">${name}</div>
            <div style="color:#888;font-size:11px">${tier}</div>
            <div style="margin-top:6px;font-size:11px;color:#888">
                ND-GAIN: <span style="color:#f0f0f0">${ndgain}</span>
                &nbsp;&nbsp;
                Renewables: <span style="color:#00c896">${renewable}</span>
            </div>`;
        tt.style.left = (event.clientX + 16) + "px";
        tt.style.top  = (event.clientY - 10) + "px";
        tt.classList.add("visible");
    }

    function hideTooltip() {
        const tt = document.getElementById("globe-tooltip");
        if (tt) tt.classList.remove("visible");
    }

    function moveTooltip(event) {
        const tt = document.getElementById("globe-tooltip");
        if (tt && tt.classList.contains("visible")) {
            tt.style.left = (event.clientX + 16) + "px";
            tt.style.top  = (event.clientY - 10) + "px";
        }
    }

    function openPanel(iso) {
        const panel = document.getElementById("country-panel-overlay");
        if (panel) panel.classList.add("open");

        function trySetInput(attempts) {
            const wrapper  = document.getElementById("d3-click-input");
            const nativeEl = wrapper;
            if (nativeEl) {
                const setter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, "value"
                ).set;
                setter.call(nativeEl, iso);
                nativeEl.dispatchEvent(new Event("input", { bubbles: true }));
                console.log("Sent to Dash:", iso);
            } else if (attempts > 0) {
                setTimeout(function() { trySetInput(attempts - 1); }, 150);
            } else {
                console.warn("d3-click-input not found after retries");
            }
        }
        trySetInput(20);
    }

    function closePanel() {
        const panel = document.getElementById("country-panel-overlay");
        if (panel) panel.classList.remove("open");
        state.selectedISO = null;
        if (state.countries) {
            state.countries
                .style("stroke", CONFIG.colours.border)
                .style("stroke-width", "0.3px");
        }
    }

    function openTerritoryPanel(iso, name) {
        const panel = document.getElementById("country-panel-overlay");
        if (panel) panel.classList.add("open");
        const input = document.getElementById("d3-click-input");
        if (input) {
            const setter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, "value"
            ).set;
            setter.call(input, "TERRITORY:" + iso + ":" + name);
            input.dispatchEvent(new Event("input", { bubbles: true }));
        }
    }

    function startRotation() { state.rotating = true; }

    function stopRotation() {
        state.rotating = false;
        clearTimeout(state.rotateTimer);
        state.rotateTimer = setTimeout(startRotation, CONFIG.rotateDelay);
    }

    function buildISOLookup() {
        // String zero-padded numeric IDs matching TopoJSON world-110m
        return {
            "004":"AFG",
            "008":"ALB",
            "010":"ATA",
            "012":"DZA",
            "024":"AGO",
            "031":"AZE",
            "032":"ARG",
            "036":"AUS",
            "040":"AUT",
            "044":"BHS",
            "050":"BGD",
            "051":"ARM",
            "056":"BEL",
            "064":"BTN",
            "068":"BOL",
            "070":"BIH",
            "072":"BWA",
            "076":"BRA",
            "084":"BLZ",
            "090":"SLB",
            "096":"BRN",
            "100":"BGR",
            "104":"MMR",
            "108":"BDI",
            "112":"BLR",
            "116":"KHM",
            "120":"CMR",
            "124":"CAN",
            "140":"CAF",
            "144":"LKA",
            "148":"TCD",
            "152":"CHL",
            "156":"CHN",
            "158":"TWN",
            "170":"COL",
            "178":"COG",
            "180":"COD",
            "188":"CRI",
            "191":"HRV",
            "192":"CUB",
            "196":"CYP",
            "203":"CZE",
            "204":"BEN",
            "208":"DNK",
            "214":"DOM",
            "218":"ECU",
            "222":"SLV",
            "226":"GNQ",
            "231":"ETH",
            "232":"ERI",
            "233":"EST",
            "238":"FLK",
            "242":"FJI",
            "246":"FIN",
            "250":"FRA",
            "260":"ATF",
            "262":"DJI",
            "266":"GAB",
            "268":"GEO",
            "270":"GMB",
            "275":"PSE",
            "276":"DEU",
            "288":"GHA",
            "300":"GRC",
            "304":"GRL",
            "320":"GTM",
            "324":"GIN",
            "328":"GUY",
            "332":"HTI",
            "340":"HND",
            "348":"HUN",
            "352":"ISL",
            "356":"IND",
            "360":"IDN",
            "364":"IRN",
            "368":"IRQ",
            "372":"IRL",
            "376":"ISR",
            "380":"ITA",
            "384":"CIV",
            "388":"JAM",
            "392":"JPN",
            "398":"KAZ",
            "400":"JOR",
            "404":"KEN",
            "408":"PRK",
            "410":"KOR",
            "414":"KWT",
            "417":"KGZ",
            "418":"LAO",
            "422":"LBN",
            "426":"LSO",
            "428":"LVA",
            "430":"LBR",
            "434":"LBY",
            "440":"LTU",
            "442":"LUX",
            "450":"MDG",
            "454":"MWI",
            "458":"MYS",
            "466":"MLI",
            "478":"MRT",
            "484":"MEX",
            "496":"MNG",
            "498":"MDA",
            "499":"MNE",
            "504":"MAR",
            "508":"MOZ",
            "512":"OMN",
            "516":"NAM",
            "524":"NPL",
            "528":"NLD",
            "540":"NCL",
            "548":"VUT",
            "554":"NZL",
            "558":"NIC",
            "562":"NER",
            "566":"NGA",
            "578":"NOR",
            "586":"PAK",
            "591":"PAN",
            "598":"PNG",
            "600":"PRY",
            "604":"PER",
            "608":"PHL",
            "616":"POL",
            "620":"PRT",
            "624":"GNB",
            "626":"TLS",
            "630":"PRI",
            "634":"QAT",
            "642":"ROU",
            "643":"RUS",
            "646":"RWA",
            "682":"SAU",
            "686":"SEN",
            "688":"SRB",
            "694":"SLE",
            "703":"SVK",
            "704":"VNM",
            "705":"SVN",
            "706":"SOM",
            "710":"ZAF",
            "716":"ZWE",
            "724":"ESP",
            "728":"SSD",
            "729":"SDN",
            "732":"ESH",
            "740":"SUR",
            "748":"SWZ",
            "752":"SWE",
            "756":"CHE",
            "760":"SYR",
            "762":"TJK",
            "764":"THA",
            "768":"TGO",
            "780":"TTO",
            "784":"ARE",
            "788":"TUN",
            "792":"TUR",
            "795":"TKM",
            "800":"UGA",
            "804":"UKR",
            "807":"MKD",
            "818":"EGY",
            "826":"GBR",
            "834":"TZA",
            "840":"USA",
            "854":"BFA",
            "858":"URY",
            "860":"UZB",
            "862":"VEN",
            "887":"YEM",
            "894":"ZMB"
        };
    }

    function initGlobe(worldData, countryData) {
        state.countryData = countryData;
        const container = document.getElementById("globe-container");
        if (!container) {
            console.error("Globe container not found");
            return;
        }

        const W = window.innerWidth;
        const H = window.innerHeight;
        const R = Math.min(W, H) * 0.42;

        state.projection = d3.geoOrthographic()
            .scale(R)
            .translate([W / 2, H / 2])
            .clipAngle(90)
            .rotate([0, -20, 0]);

        state.path = d3.geoPath().projection(state.projection);

        state.svg = d3.select("#globe-container")
            .append("svg")
            .attr("id", "globe-svg")
            .attr("width", W)
            .attr("height", H);

        state.svg.append("circle")
            .attr("class", "sphere")
            .attr("cx", W / 2).attr("cy", H / 2).attr("r", R)
            .style("fill", CONFIG.colours.ocean);

        state.svg.append("circle")
            .attr("class", "globe-glow")
            .attr("cx", W / 2).attr("cy", H / 2).attr("r", R);

        const graticule = d3.geoGraticule()();
        state.svg.append("path")
            .datum(graticule)
            .attr("class", "graticule")
            .attr("d", state.path)
            .style("stroke", CONFIG.colours.graticule);

        const countries  = topojson.feature(worldData, worldData.objects.countries);
        const isoLookup  = buildISOLookup();

        state.countries = state.svg.selectAll(".country")
            .data(countries.features)
            .enter()
            .append("path")
            .attr("class", "country")
            .attr("d", state.path)
            .style("fill", function(d) {
                const iso = isoLookup[d.id];
                return iso ? getTierColour(iso) : CONFIG.colours.noData;
            })
            .style("stroke", CONFIG.colours.border)
            .style("stroke-width", "0.3px")
            .on("mouseover", function(event, d) {
                const iso  = isoLookup[d.id];
                const name = getDisplayName(iso, countryData);
                d3.select(this)
                  .style("stroke", CONFIG.colours.hover)
                  .style("stroke-width", "0.8px");
                showTooltip(event, iso, name);
            })
            .on("mousemove", moveTooltip)
            .on("mouseout", function(event, d) {
                const iso        = isoLookup[d.id];
                const isSelected = state.selectedISO === iso;
                d3.select(this)
                  .style("stroke", isSelected
                         ? CONFIG.colours.selected : CONFIG.colours.border)
                  .style("stroke-width", isSelected ? "1.2px" : "0.3px");
                hideTooltip();
            })
            .on("click", function(event, d) {
                const iso = isoLookup[d.id];
                if (!iso) return;
                stopRotation();
                hideTooltip();
                state.countries
                    .style("stroke", CONFIG.colours.border)
                    .style("stroke-width", "0.3px");
                state.selectedISO = iso;
                d3.select(this)
                  .style("stroke", CONFIG.colours.selected)
                  .style("stroke-width", "1.5px");

                // Only open panel for countries in NDC database
                const hasNDC = state.countryData[iso] !== undefined;
                if (hasNDC) {
                    openPanel(iso);
                } else {
                    // Show territory panel with just the name
                    openTerritoryPanel(iso, getDisplayName(iso, state.countryData));
                }
            });

        const drag = d3.drag()
            .on("start", function() { stopRotation(); })
            .on("drag", function(event) {
                const rotate = state.projection.rotate();
                const newLon = rotate[0] + event.dx * CONFIG.sensitivity;
                const newLat = Math.max(-90, Math.min(90,
                               rotate[1] - event.dy * CONFIG.sensitivity));
                state.projection.rotate([newLon, newLat, rotate[2]]);
                updatePaths();
            });

        const zoom = d3.zoom()
            .scaleExtent([CONFIG.zoomMin, CONFIG.zoomMax])
            .on("zoom", function(event) {
                stopRotation();
                state.scale = event.transform.k;
                const R_new = Math.min(W, H) * 0.42 * state.scale;
                state.projection.scale(R_new);
                state.svg.select(".sphere").attr("r", R_new);
                state.svg.select(".globe-glow").attr("r", R_new);
                updatePaths();
            });

        state.svg.call(drag).call(zoom);

        d3.timer(function() {
            if (!state.rotating) return;
            const rotate = state.projection.rotate();
            state.projection.rotate([
                rotate[0] + CONFIG.autoRotateSpeed,
                rotate[1], rotate[2]
            ]);
            updatePaths();
        });

        window.addEventListener("resize", function() {
            const W2 = window.innerWidth;
            const H2 = window.innerHeight;
            const R2 = Math.min(W2, H2) * 0.42 * state.scale;
            state.projection.scale(R2).translate([W2 / 2, H2 / 2]);
            state.svg.attr("width", W2).attr("height", H2);
            state.svg.select(".sphere")
                .attr("cx", W2/2).attr("cy", H2/2).attr("r", R2);
            state.svg.select(".globe-glow")
                .attr("cx", W2/2).attr("cy", H2/2).attr("r", R2);
            updatePaths();
        });

        console.log("Globe initialised with", countries.features.length, "countries");
    }

    function updatePaths() {
        if (!state.path || !state.svg) return;
        state.svg.selectAll(".country").attr("d", state.path);
        state.svg.selectAll(".graticule").attr("d", state.path);
    }

    function updateColourMode(mode, countryData) {
        if (!state.countries) return;
        const isoLookup = buildISOLookup();
        state.countries.style("fill", function(d) {
            const iso = isoLookup[d.id];
            if (!iso || !countryData[iso]) return CONFIG.colours.noData;
            const cd = countryData[iso];
            if (mode === "tier_score") return getTierColour(iso);
            if (mode === "ndgain_score") {
                const v = parseFloat(cd.ndgain_score);
                if (isNaN(v)) return CONFIG.colours.noData;
                return interpolateRdYlGn(Math.max(0, Math.min(1,(v-20)/55)));
            }
            if (mode === "vulnerability_score") {
                const v = parseFloat(cd.vulnerability_score);
                if (isNaN(v)) return CONFIG.colours.noData;
                return interpolateRdYlGn(1 - Math.max(0,Math.min(1,(v-0.2)/0.5)));
            }
            if (mode === "renewable_electricity_pct") {
                const v = parseFloat(cd.renewable_electricity_pct);
                if (isNaN(v)) return CONFIG.colours.noData;
                const t = Math.max(0, Math.min(1, v / 100));
                const r = Math.round(26 + t * (0 - 26));
                const g = Math.round(26 + t * (200 - 26));
                const b = Math.round(26 + t * (150 - 26));
                return "rgb(" + r + "," + g + "," + b + ")";
            }
            return CONFIG.colours.noData;
        });
    }

    function interpolateRdYlGn(t) {
        if (t < 0.5) {
            return "rgb(192," + Math.round(57 + t*2*(231-57)) + ",43)";
        } else {
            const r = Math.round(231 + (t-0.5)*2*(0-231));
            const g = Math.round(231 + (t-0.5)*2*(200-231));
            const b = Math.round(43  + (t-0.5)*2*(150-43));
            return "rgb(" + r + "," + g + "," + b + ")";
        }
    }

    function bootstrap() {
        const d3Script    = document.createElement("script");
        d3Script.src      = "https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js";
        d3Script.onload   = function() {
            const topoScript  = document.createElement("script");
            topoScript.src    = "https://cdnjs.cloudflare.com/ajax/libs/topojson/3.0.2/topojson.min.js";
            topoScript.onload = function() { waitForContainer(40); };
            document.head.appendChild(topoScript);
        };
        document.head.appendChild(d3Script);
    }

    function waitForContainer(attempts) {
        const container = document.getElementById("globe-container");
        if (container) {
            loadDataAndInit();
        } else if (attempts > 0) {
            setTimeout(function() { waitForContainer(attempts - 1); }, 250);
        } else {
            console.error("Globe container not found after waiting");
        }
    }

    function loadDataAndInit() {
        fetch("/assets/world-110m.json")
            .then(function(r) { return r.json(); })
            .then(function(worldData) {
                fetch("/country-data")
                    .then(function(r) { return r.json(); })
                    .then(function(countryData) {
                        initGlobe(worldData, countryData);
                        setupColourModeListener(countryData);
                        setupClosePanelListener();
                    })
                    .catch(function(err) {
                        console.error("Country data error:", err);
                        initGlobe(worldData, {});
                    });
            })
            .catch(function(err) { console.error("World data error:", err); });
    }

    function setupColourModeListener(countryData) {
        setInterval(function() {
            const wrapper = document.getElementById("colour-mode-value");
            if (!wrapper) return;
            const input = wrapper;
            if (!input) return;
            const mode = input ? input.value : null;
            if (mode && mode !== state.lastColourMode) {
                state.lastColourMode = mode;
                updateColourMode(mode, countryData);
            }
        }, 300);
    }

    function setupClosePanelListener() {
        document.addEventListener("click", function(e) {
            if (e.target && (
                e.target.id === "close-panel-btn" ||
                (e.target.closest && e.target.closest("#close-panel-btn"))
            )) {
                closePanel();
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bootstrap);
    } else {
        setTimeout(bootstrap, 300);
    }

    window.NDCGlobe = { updateColourMode, closePanel };

    // Hide controls and scroll hint based on scroll position
    window.addEventListener("scroll", function() {
        const scrolled   = window.scrollY;
        const windowH    = window.innerHeight;
        const docH       = document.documentElement.scrollHeight;
        const controls   = document.getElementById("globe-controls");
        const scrollHint = document.getElementById("scroll-hint");
        const pastGlobe  = scrolled > windowH * 0.6;
        const nearBottom = (scrolled + windowH) >= (docH - 100);

        if (controls) {
            controls.style.opacity       = pastGlobe ? "0" : "1";
            controls.style.pointerEvents = pastGlobe ? "none" : "all";
            controls.style.transition    = "opacity 0.3s ease";
        }
        if (scrollHint) {
            const hideHint = pastGlobe || nearBottom;
            if (hideHint) {
                scrollHint.classList.add("hidden");
            } else {
                scrollHint.classList.remove("hidden");
            }
        }
    });

    // Rotation toggle click handler
    function setupRotationToggle() {
        const btn = document.getElementById("rotation-toggle");
        if (!btn) {
            setTimeout(setupRotationToggle, 500);
            return;
        }
        btn.addEventListener("click", function() {
            if (state.rotating) {
                stopRotation();
                clearTimeout(state.rotateTimer);
                state.rotating    = false;
                btn.textContent   = "▶ Resume";
                btn.style.color   = "#e67e22";
                btn.style.border  = "1px solid #e67e2240";
                btn.style.backgroundColor = "#e67e2210";
            } else {
                state.rotating    = true;
                btn.textContent   = "⏸ Pause";
                btn.style.color   = "#00c896";
                btn.style.border  = "1px solid #00c89640";
                btn.style.backgroundColor = "#00c89610";
            }
        });
    }
    setupRotationToggle();

    // Close panel on outside click
    document.addEventListener("click", function(e) {
        const panel   = document.getElementById("country-panel-overlay");
        const isOpen  = panel && panel.classList.contains("open");
        if (!isOpen) return;

        const clickedInsidePanel = panel.contains(e.target);
        const clickedOnGlobe    = e.target.closest("#globe-svg") ||
                                   e.target.closest(".country");
        if (!clickedInsidePanel && !clickedOnGlobe) {
            closePanel();
        }
    });

    // Auto-close panel when scrolled past globe
    window.addEventListener("scroll", function() {
        const scrolled  = window.scrollY;
        const windowH   = window.innerHeight;
        const panel     = document.getElementById("country-panel-overlay");
        const pastGlobe = scrolled > windowH * 0.8;

        if (pastGlobe && panel && panel.classList.contains("open")) {
            closePanel();
        }
    }, { passive: true });

})();
