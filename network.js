var svg = d3.select("svg"),
    width = +svg.node().getBoundingClientRect().width,
    height = +svg.node().getBoundingClientRect().height;

// svg objects
var link, node, label;
// the data - an object with nodes and links
var graph;

//get file selector
var selected_graph = "graphs/graph.json"

// load the data
d3.json(selected_graph, function(error, _graph) {
  if (error) throw error;
  graph = _graph;
  initializeDisplay();
  initializeSimulation();
});

// Load the data from the selected file
function loadGraph(file) {
    var reader = new FileReader();
    reader.onload = function(event) {
        //remove all elements from svg_group
        svg_group.selectAll("*").remove();
        //remove legend from svg
        svg.selectAll(".legend").remove();

        graph = JSON.parse(event.target.result);
        initializeDisplay();
        initializeSimulation();
    };
    reader.readAsText(file);
}

// Handle file input change
document.getElementById('fileInput').addEventListener('change', function(event) {
    var file = event.target.files[0];
    if (file) {
        loadGraph(file);
    }
});

//////////// FORCE SIMULATION //////////// 

// force simulator
var simulation = d3.forceSimulation();

// set up the simulation and event to update locations after each tick
function initializeSimulation() {
  simulation.nodes(graph.nodes);
  initializeForces();
  simulation.on("tick", ticked);
}

// values for all forces
forceProperties = {
    center: {
        x: 0.5,
        y: 0.5
    },
    charge: {
        enabled: true,
        strength: -30,
        distanceMin: 1,
        distanceMax: 2000
    },
    collide: {
        enabled: true,
        strength: .7,
        iterations: 1,
        radius: 5
    },
    forceX: {
        enabled: true,
        strength: .1,
        x: .5
    },
    forceY: {
        enabled: true,
        strength: .1,
        y: .5
    },
    link: {
        enabled: true,
        distance: 30,
        iterations: 1
    },
    label:{
        enabled: false,
        font:{
            size: 10,
            color: "black",
            weight: "normal",
            style: "normal"
        }
    }
}

// add forces to the simulation
function initializeForces() {
    // add forces and associate each with a name
    simulation
        .force("link", d3.forceLink())
        .force("charge", d3.forceManyBody())
        .force("collide", d3.forceCollide())
        .force("center", d3.forceCenter())
        .force("forceX", d3.forceX())
        .force("forceY", d3.forceY());
    // apply properties to each of the forces
    updateForces();
}

// apply new force properties
function updateForces() {
    // get each force by name and update the properties
    simulation.force("center")
        .x(width * forceProperties.center.x)
        .y(height * forceProperties.center.y);
    simulation.force("charge")
        .strength(forceProperties.charge.strength * forceProperties.charge.enabled)
        .distanceMin(forceProperties.charge.distanceMin)
        .distanceMax(forceProperties.charge.distanceMax);
    simulation.force("collide")
        .strength(forceProperties.collide.strength * forceProperties.collide.enabled)
        .radius(forceProperties.collide.radius)
        .iterations(forceProperties.collide.iterations);
    simulation.force("forceX")
        .strength(forceProperties.forceX.strength * forceProperties.forceX.enabled)
        .x(width * forceProperties.forceX.x);
    simulation.force("forceY")
        .strength(forceProperties.forceY.strength * forceProperties.forceY.enabled)
        .y(height * forceProperties.forceY.y);
    simulation.force("link")
        .id(function(d) {return d.id;})
        .distance(forceProperties.link.distance)
        .iterations(forceProperties.link.iterations)
        .links(forceProperties.link.enabled ? graph.links : []);

    // updates ignored until this is run
    // restarts the simulation (important if simulation has already slowed down)
    simulation.alpha(1).restart();
}

//////////// Zoom ////////////

var transform = d3.zoomIdentity;

svg_group = svg.append("g");

const zoomable = d3.zoom().on("zoom", function() {
    svg_group.attr("transform", d3.event.transform);
});

svg.call(zoomable);

// Define the marker element
svg.append("defs").append("marker")
    .attr("id", "arrowhead")
    .attr("viewBox", "-0 -5 10 10")
    .attr("refX", 13) // Adjust this value to position the arrowhead correctly
    .attr("refY", 0)
    .attr("orient", "auto")
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("xoverflow", "visible")
    .append("svg:path")
    .attr("d", "M 0,-5 L 10 ,0 L 0,5")
    .attr("fill", "#999")
    .style("stroke", "none");

//////////// DISPLAY ////////////

// generate the svg objects and force simulation
function initializeDisplay() {
  // set the data and properties of link lines
  link = svg_group.append("g")
        .attr("class", "links")
    .selectAll("line")
    .data(graph.links)
    .enter().append("line")
    .attr("marker-end", "url(#arrowhead)"); // Add this line to use the marker

  // set the data and properties of node circles
  node = svg_group.append("g")
        .attr("class", "nodes")
    .selectAll("circle")
    .data(graph.nodes)
    .enter()
    .append("circle")
    .style("fill", function(d) { return d3.schemeCategory10[d.group % 10]; })
    .style("stroke", "black")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

    node.append("title")
    .text(function(d) { 
        return Object.entries(d)
            .map(([key, value]) => `${key}: ${value}`)
            .join("\n"); 
    });

    // Append text elements to display node IDs
    labels = svg_group.append("g")
    .attr("class", "labels")
    .selectAll("text")
    .data(graph.nodes)
    .enter()
    .append("text")
    .attr("x", function(d) { return d.x; })
    .attr("y", function(d) { return d.y; }) // Position above the circle
    .attr("text-anchor", "middle")
    .attr("font-size", "10px")
    .text(function(d) { return d.id; })
    .attr("fill", "black");

 console.log(graph.nodes)

  // visualize the graph
  updateDisplay();

  // Extract unique groups from the data
    var groups = [...new Set(graph.nodes.map(d => d.group))];

    // Create a legend container
    var legend = svg.append("g")
    .attr("class", "legend")
    .attr("transform", "translate(20, 20)");

    // Define padding
    var padding = 10;

    // Calculate legend dimensions
    var legendItemHeight = 20;
    var legendWidth = 100; // Adjust as needed
    var legendHeight = groups.length * legendItemHeight;

    // Append border around the legend
    legend.append("rect")
    .attr("width", legendWidth + 2 * padding)
    .attr("height", legendHeight + 2 * padding)
    .attr("fill", "white")
    .attr("stroke", "black");

    // Append legend items with padding
    groups.forEach((group, i) => {
        var legendItem = legend.append("g")
            .attr("class", "legend-item")
            .attr("transform", `translate(${padding}, ${i * legendItemHeight + padding})`);

        // Append color box
        legendItem.append("rect")
            .attr("width", 18)
            .attr("height", 18)
            .attr("fill", d3.schemeCategory10[group % 10]);

       
        var groupNames = {
            1: "IP",
            2: "Host",
            3: "Vulnerability",
            4: "ASN",
            5: "Product"
        };

        // Append text label with group name
        legendItem.append("text")
            .attr("x", 24)
            .attr("y", 9)
            .attr("dy", "0.35em")
            .text(groupNames[group] || `Group ${group}`);
        });
}

// update the display based on the forces (but not positions)
function updateDisplay() {
    //transform all elements in svg by the transform object

    node
        .attr("r", forceProperties.collide.radius)
        .attr("stroke", forceProperties.charge.strength > 0 ? "blue" : "red")
        .attr("stroke-width", forceProperties.charge.enabled==false ? 0 : Math.abs(forceProperties.charge.strength)/15);

    labels
        .attr("visibility", forceProperties.label.enabled ? "visible" : "hidden")
        .attr("font-size", forceProperties.label.font.size + "px")
        .attr("font-weight", forceProperties.label.font.weight)
        .attr("font-style", forceProperties.label.font.style)
        .attr("fill", forceProperties.label.font.color);

    link
        .attr("stroke-width", forceProperties.link.enabled ? 1 : .5)
        .attr("opacity", forceProperties.link.enabled ? 1 : 0);
}



// update the display positions after each simulation tick
function ticked() {
    link
        .attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    labels
        .attr("x", function(d) { return d.x; })
        .attr("y", function(d) { return d.y; }); // Position above the circle

    node
        .attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });
    d3.select('#alpha_value').style('flex-basis', (simulation.alpha()*100) + '%');
}



//////////// UI EVENTS ////////////

function dragstarted(d) {
  if (!d3.event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(d) {
  d.fx = d3.event.x;
  d.fy = d3.event.y;
}

function dragended(d) {
  if (!d3.event.active) simulation.alphaTarget(0.0001);
  d.fx = null;
  d.fy = null;
}

// update size-related forces
d3.select(window).on("resize", function(){
    width = +svg_group.node().getBoundingClientRect().width;
    height = +svg_group.node().getBoundingClientRect().height;
    updateForces();
});

// convenience function to update everything (run after UI input)
function updateAll() {
    updateForces();
    updateDisplay();
}


