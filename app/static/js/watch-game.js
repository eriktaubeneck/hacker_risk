//;(function(exports){

    var gameLog = []; 
    var nodeList = []; 
    var linkList = [];
    var playerList = {}; 
    var colors = d3.shuffle(["#66FFFF", "#33FF33", "#FFFF4D", "#FF66CC", "#FFA366", "#C299C2"]); 
    var gameID; 
    var broadcasts; 
    var force; 
    
    //fixed positions for overlay onto risk board
    var fixedPositions = 
        "alaska" : {x: 50, y:30, forced:true},
        "northwest territory" : {x: 150, y:70},
        "kamchatka" : {x: 700, y:30, forced:true},
        "central america" : {x: 130, y:250},
        "central africa" : {x: 400, y:375},
        "north africa" : {x: 344, y:304, forced:true},
        "eastern united states" : {x: 175, y:190, forced:true},
        "western united states" : {x: 120, y:175, forced:true},
        "greenland" : {x: 250, y:50, forced:true},
        "indonesia" : {x: 600, y:375},
        "eastern australia" : {x: 690, y:410},
        "western australia" : {x: 630, y:440, forced:true},
        "new guinea" : {x: 690, y:350},
        "alberta" : {x: 115, y:125},
        "ontario" : {x: 175, y:135},
        "eastern canada" : {x: 230, y:125},
        "brazil" : {x: 238, y:332, forced:true},
        "india" : {x: 550, y:280, forced:true},
        "afghanistan" : {x: 500, y:200},
        "middle east" : {x: 450, y:250},
        "southeast asia" : {x: 615, y:290},
        "madagascar" : {x: 475, y:440, forced:true},
        "argentina" : {x: 190, y:415, forced:true},
        "yakutsk" : {x: 600, y:65},
        "japan" : {x: 685, y:180, forced:true},
        "china" : {x: 590, y:230},
        "mongolia" : {x: 610, y:180},
        "ural" : {x: 515, y:130},
        "irkutsk" : {x: 595, y:115},
        "siberia" : {x: 550, y:80},
        "russia" : {x: 450, y:140, forced:true},
        "iceland" : {x: 320, y:85},
        "northern europe" : {x: 375, y:170},
        "southern europe" : {x: 375, y:215},
        "south africa" : {x: 400, y:440, forced:true},
        "western europe" : {x: 325, y:230},
        "great britain" : {x: 300, y:165, forced:true},
        "scandinavia" : {x: 385, y:85, forced:true},
        "east africa" : {x: 450, y:350},
        "venezuela" : {x:185, y:278},
        "peru" : {x:170, y:350},
        "egypt" : {x:400, y:290},
    };
    
    var startFromDB = function () {
        makeSlider(); 
        initializeStatusDisplay(); 
    };

    $(document).ready(function(){
        createGraph(doStuff); 
        startFromDB(); 
    });

    var createGraph = function (callback) {
        $.getJSON("/static/board_graph.json", function(data) {
            //add nodes (countries) first
            $.each(data, function (key, continent) {
                var countries = continent["countries"]; 
                $.each(countries, function(name, data) {
                    var node = {};
                    node.name = name;
                    var borderCountries = data["border countries"];
                    if (fixedPositions[node.name]) {
                        node.x=fixedPositions[node.name]["x"]; 
                        node.y=fixedPositions[node.name]["y"]; 
                        node.fixed=fixedPositions[node.name]["forced"] || false; 
                    }
                    node.continent = key; 
                    node.owner = null; 
                    node.troops = 0;
                    node.borderCountries = borderCountries; 
                    nodeList.push(node);
                });
            });
            console.log("node list created"); 

            //then create links between them based on border countries
            for (var i = 0; i<nodeList.length; i++) {
                var node = nodeList[i]; 
                borderCountries = node.borderCountries; 
                for (var j = 0; j<borderCountries.length; j++) {
                    for (var k = 0; k<nodeList.length; k++) {
                        if (nodeList[k].name == borderCountries[j]) {
                            var link = {};
                            link.source = i; 
                            link.target = k; 
                            var linkExists = false; 
                            for (var l=0; l<linkList.length; l++) {
                                if (link.source == linkList[l].target && link.target == linkList[l].source) {
                                    linkExists = true; 
                                }
                            } 
                            if (!linkExists) {
                                linkList.push(link); 
                            }
                        }
                    }
                }
            }
            console.log("link list created"); 
            callback();
        });  
    }
    
    var initializeStatusDisplay = function() {
        d3.json("/game/" + gameID + "/1", function(data) {
            var players = data["players"]; 
            var index = 0; 
            for (player in players) {
                playerList[player] = index; 
                index ++; 
                var playerDiv = d3.select("#gameStats").append("div")
                    .text(player + ": cards: " + players[player]["card"]) 
                    .style("color", colors[playerList[player]]) 
                    .attr("id", player.split(" ").join(""));
            });
            var lastAction = d3.select("#gameStats").append("div")
                .text("Last Action")
                .attr("id", "lastAction"); 
        };
    };
        
    function doStuff() {    
        var height = 500; 
        var width = 800; 

        force = d3.layout.force()
            .nodes(nodeList)
            .links(linkList)
            .size([width, height])
            .linkDistance(30)
            .charge(-500)
            .linkStrength(0.7)
            .on("tick", tick)
            .start(); 
            
        // Create D3 Layout Container
        var svg = d3.select("#map").append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("style", "z-index: 1")
            .attr("id", "d3Layout"); 
   
        //Create br so background image is positioned correctly
        d3.select("#map").append("br"); 
 
        //create element for risk board background image
        var background = d3.select("#map").append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("id", "background"); 

    //add links 
        var path = svg.append("svg:g").selectAll("path")
            .data(force.links())
            .enter().append("svg:path")
            .attr("class", "link")
    //define nodes?
        var node = svg.selectAll(".node")
            .data(force.nodes())
            .enter().append("g")
            .attr("class", "node")
            .attr("value", 0)
            .attr("owner", null)
            .attr("id", function(d) {
                var id = d.name; 
                return id.split(" ").join(""); 
            })
            .call(force.drag); 
    //add nodes?
        
        var conts = {
            "europe": "#4D4DFF",
            "asia": "#009933",
            "north america": "#000000",
            "south america": "#FF3333",
            "africa": "#FF944D",
            "australia": "#A347A3"
        };

        var circle = node.append("circle")
            .attr("r", 7)
            .attr("class", "countryCircle")
            .style("stroke", function(d) {return conts[d.continent];}); 

        //add text?
        var label = node.append("text")
            .attr("x", 12)
            .classed ("label", true)
            .style("fill", "black")
            .attr("dy", ".35em")
            .text(function(d) {return d.name;});

        // add troop count number
        var troopCount = node.append("text")
            .attr("dx", -3)
            .attr("dy", 3)
            .text(function(d) {return d.troops;}); 

        function tick() {
            path.attr("d", function(d) {
                var dx = d.target.x - d.source.x,
                    dy = d.target.y - d.source.y,
                    dr = Math.sqrt(dx * dx + dy * dy);
                return "M" + 
                    d.source.x + "," + 
                    d.source.y + "L" + 
                    d.target.x + "," + 
                    d.target.y;
            });

            circle.attr("r", function(d) {
                var troops = d.troops || 1; 
                var radius = 7 * (Math.sqrt(troops));
                return radius; 
            });
            
            node.attr("transform", function(d) { 
                return "translate(" + d.x + "," + d.y + ")"; 
            });
            
            troopCount.text(function(d) {return d.troops;}); 
            
            label.attr("x", function(d) {
                var troops = d.troops || 1; 
                var circleRadius = 7 * (Math.sqrt(troops));
                var offset = 2 + circleRadius; 
                return offset;
            }); 
        }
        console.log("graph created"); 
    }; 

    var makeSlider = function() {
        var sliderMax = broadcasts-1;
        $(function() {
            $("#play").button().click(function(event) {
                if(!$("#play").data("intervalID"))
                    $("#play").data("intervalID", play(10));    
            });
            $("#pause").button().click(function(event) {
                pause($("#play").data("intervalID"));
                $("#play").data("intervalID", null);
            });
        }); 
        $(function() {
            $("#slider").slider({
                min:0, 
                max: sliderMax,
                slide: function (event, ui) {
                    $.getJSON("/game/" + gameID + "/" + ui.value, function(data) {
                        $("#turn").text("Turn: " + data["turn"]);
                        updateNodes(data); 
                        updateStats(data); 
                    }); 
                }
            });
            $("#turn").text("Turn: 0 - Initial Deployment");
        });
    }

    var updateStats = function(game) {
        var countries = game["countries"];
        var players= game["players"];
        var lastAction = game["last_action"];
        for (player in players) {
            var playerName = player.split(" ").join("");
            var totalTroops = 0; 
            var countryCount = 0; 
            for (countryName in countries) {
                if(value["owner"] == player) {
                    countryCount++; 
                    totalTroops += countries[countryName]["troops"]; 
                }
            };
            $("#" +playerName).text(player + " -- cards: " + players[player]["cards"] + " -- troops: " + totalTroops); 
        };
        //TODO: parse last Action into 1) readable text
        //                             2) animated shit on graph
        var actions = ["deployed", "attacked", "reinforced", "defeated", "spent"];
        var pos = (actions.map(function(x) {return lastAction.indexOf(x);})); 
        var action = actions[pos.indexOf(d3.max(pos))];
        $("#lastAction").text(lastAction); 
    }

    var updateNodes = function(currentTurn) {
        var countries = currentTurn["countries"];
        var data = [];
        var currentData = d3.selectAll(".node").data();
        for (i in currentData) {
            d=currentData[i]; 
            d.owner = countries[d.name]["owner"]; 
            d.troops = countries[d.name]["troops"];
            //d.fixed=false; 
            data.push(d); 
        }
        d3.selectAll(".node").data(data, function(d) {return d.name;});
        d3.selectAll(".node").select(".countryCircle").style("fill", function(d) {return colors[playerList[d.owner]]}); 
        force.start(); 
    };

    var autoSlide = function(slideTo) {
        slideTo = slideTo || $("#slider").slider("value")+1; 
        $("#slider").slider("value", slideTo);  
        $.getJSON("/game/" + gameID + "/"+ slideTo, function(data) {
            if (data["turn"] == 0) { 
                $("#turn").text("Turn: " + data["turn"] + " - Initial Deployment");
            } else {
                $("#turn").text("Turn: " + data["turn"]);
            }
            updateNodes(data);
            updateStats(data);
        });
    };

    var play = function(speed) {
        var intervalId = window.setInterval(autoSlide, speed); 
        return intervalId; 
    };

    var pause = function(intervalId) {
        window.clearInterval(intervalId); 
    };

//})(this); 
