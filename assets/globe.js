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

    function startRotation() { state.rotating = true; }

    function stopRotation() {
        state.rotating = false;
        clearTimeout(state.rotateTimer);
        state.rotateTimer = setTimeout(startRotation, CONFIG.rotateDelay);
    }

    function buildISOLookup() {
        return {
            4:"AFG",8:"ALB",12:"DZA",24:"AGO",28:"ATG",
            32:"ARG",36:"AUS",40:"AUT",50:"BGD",52:"BRB",
            56:"BEL",64:"BTN",68:"BOL",70:"BIH",72:"BWA",
            76:"BRA",84:"BLZ",90:"SLB",96:"BRN",100:"BGR",
            104:"MMR",108:"BDI",116:"KHM",120:"CMR",124:"CAN",
            132:"CPV",140:"CAF",144:"LKA",152:"CHL",156:"CHN",
            170:"COL",174:"COM",180:"COD",178:"COG",184:"COK",
            188:"CRI",191:"HRV",192:"CUB",196:"CYP",203:"CZE",
            204:"BEN",208:"DNK",262:"DJI",212:"DMA",214:"DOM",
            218:"ECU",818:"EGY",222:"SLV",226:"GNQ",232:"ERI",
            231:"ETH",242:"FJI",246:"FIN",250:"FRA",266:"GAB",
            270:"GMB",268:"GEO",276:"DEU",288:"GHA",300:"GRC",
            308:"GRD",320:"GTM",324:"GIN",624:"GNB",328:"GUY",
            332:"HTI",340:"HND",348:"HUN",356:"IND",360:"IDN",
            364:"IRN",368:"IRQ",372:"IRL",376:"ISR",380:"ITA",
            388:"JAM",392:"JPN",400:"JOR",398:"KAZ",404:"KEN",
            296:"KIR",408:"PRK",410:"KOR",414:"KWT",417:"KGZ",
            418:"LAO",422:"LBN",426:"LSO",430:"LBR",434:"LBY",
            440:"LTU",442:"LUX",450:"MDG",454:"MWI",458:"MYS",
            462:"MDV",466:"MLI",470:"MLT",584:"MHL",478:"MRT",
            480:"MUS",484:"MEX",583:"FSM",496:"MNG",504:"MAR",
            508:"MOZ",516:"NAM",520:"NRU",524:"NPL",528:"NLD",
            554:"NZL",558:"NIC",562:"NER",566:"NGA",578:"NOR",
            512:"OMN",586:"PAK",585:"PLW",591:"PAN",598:"PNG",
            600:"PRY",604:"PER",608:"PHL",616:"POL",620:"PRT",
            634:"QAT",642:"ROU",643:"RUS",646:"RWA",659:"KNA",
            662:"LCA",670:"VCT",882:"WSM",674:"SMR",678:"STP",
            682:"SAU",686:"SEN",694:"SLE",703:"SVK",705:"SVN",
            706:"SOM",710:"ZAF",724:"ESP",729:"SDN",740:"SUR",
            748:"SWZ",752:"SWE",756:"CHE",760:"SYR",762:"TJK",
            764:"THA",626:"TLS",768:"TGO",776:"TON",780:"TTO",
            788:"TUN",792:"TUR",795:"TKM",798:"TUV",800:"UGA",
            804:"UKR",784:"ARE",826:"GBR",834:"TZA",840:"USA",
            858:"URY",860:"UZB",548:"VUT",862:"VEN",704:"VNM",
            887:"YEM",894:"ZMB",716:"ZWE",275:"PSE",807:"MKD",
            499:"MNE",688:"SRB",706:"SOM",352:"ISL",492:"MCO",
            336:"VAT",570:"NIU",
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
                const name = iso && countryData[iso]
                             ? countryData[iso].display_name || iso
                             : "Unknown";
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
                openPanel(iso);
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

})();
