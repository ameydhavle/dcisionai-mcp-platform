import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { BarChart3, X } from 'lucide-react';

const DecisionLandscape3D = ({ result, onClose }) => {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const controlsRef = useRef(null);
  const animationRef = useRef(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [landscapeData, setLandscapeData] = useState(null);

  const loadLandscapeData = async () => {
    try {
      const response = await fetch('https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod/3d-landscape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          optimization_result: result,
          resolution: 50
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        setLandscapeData(data.landscape_data);
      }
    } catch (error) {
      console.error('Failed to load landscape data:', error);
    }
  };

  useEffect(() => {
    if (!mountRef.current) return;

    // Load landscape data from backend
    loadLandscapeData();

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0a);
    sceneRef.current = scene;

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      75,
      mountRef.current.clientWidth / mountRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(10, 10, 10);

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    mountRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controlsRef.current = controls;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 5);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    // Create decision landscape
    createDecisionLandscape(scene, result, landscapeData);

    // Animation loop
    const animate = () => {
      animationRef.current = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    setIsLoaded(true);

    // Cleanup
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [result]);

  // Recreate landscape when landscapeData is loaded
  useEffect(() => {
    if (landscapeData && sceneRef.current) {
      createDecisionLandscape(sceneRef.current, result, landscapeData);
    }
  }, [landscapeData]);

  const createDecisionLandscape = (scene, result, landscapeData) => {
    // Clear existing landscape
    const existingLandscape = scene.getObjectByName('decisionLandscape');
    if (existingLandscape) {
      scene.remove(existingLandscape);
    }

    const landscapeGroup = new THREE.Group();
    landscapeGroup.name = 'decisionLandscape';

    // Create objective function as terrain using real data
    if (landscapeData && landscapeData.terrain) {
      const terrainGeometry = createTerrainGeometryFromData(landscapeData.terrain);
      const terrainMaterial = new THREE.MeshLambertMaterial({
        color: 0x1a4d3a,
        wireframe: false,
        transparent: true,
        opacity: 0.8
      });
      const terrain = new THREE.Mesh(terrainGeometry, terrainMaterial);
      terrain.receiveShadow = true;
      landscapeGroup.add(terrain);
    } else {
      // Fallback to original method
      const objectiveValue = result.optimization_solution?.objective_value || 100;
      const terrainGeometry = createTerrainGeometry(objectiveValue);
      const terrainMaterial = new THREE.MeshLambertMaterial({
        color: 0x1a4d3a,
        wireframe: false,
        transparent: true,
        opacity: 0.8
      });
      const terrain = new THREE.Mesh(terrainGeometry, terrainMaterial);
      terrain.receiveShadow = true;
      landscapeGroup.add(terrain);
    }

    // Create constraints as walls using real data
    if (landscapeData && landscapeData.constraints) {
      landscapeData.constraints.forEach((constraintData, index) => {
        const wall = createConstraintWallFromData(constraintData);
        landscapeGroup.add(wall);
      });
    } else {
      const constraints = result.model_building?.constraints || [];
      constraints.forEach((constraint, index) => {
        const wall = createConstraintWall(constraint, index);
        landscapeGroup.add(wall);
      });
    }

    // Create optimal solution as glowing beacon using real data
    if (landscapeData && landscapeData.optimal_point) {
      const optimalPoint = createOptimalSolutionBeaconFromData(landscapeData.optimal_point);
      landscapeGroup.add(optimalPoint);
    } else {
      const optimalPoint = createOptimalSolutionBeacon(result.optimization_solution);
      landscapeGroup.add(optimalPoint);
    }

    // Create variables as nodes using real data
    if (landscapeData && landscapeData.variables) {
      landscapeData.variables.forEach((variableData, index) => {
        const node = createVariableNodeFromData(variableData);
        landscapeGroup.add(node);
      });
    } else {
      const variables = result.model_building?.variables || [];
      variables.forEach((variable, index) => {
        const node = createVariableNode(variable, index);
        landscapeGroup.add(node);
      });
    }

    // Create solution path
    const solutionPath = createSolutionPath(result.optimization_solution);
    landscapeGroup.add(solutionPath);

    // Add particle system for data flow
    const particles = createDataFlowParticles(result.data_analysis);
    landscapeGroup.add(particles);

    scene.add(landscapeGroup);
  };

  const createTerrainGeometryFromData = (terrainData) => {
    const geometry = new THREE.PlaneGeometry(20, 20, terrainData.resolution - 1, terrainData.resolution - 1);
    const vertices = geometry.attributes.position.array;
    
    // Apply real height data
    for (let i = 0; i < terrainData.resolution; i++) {
      for (let j = 0; j < terrainData.resolution; j++) {
        const vertexIndex = (i * terrainData.resolution + j) * 3;
        vertices[vertexIndex + 2] = terrainData.heights[i][j];
      }
    }
    
    geometry.attributes.position.needsUpdate = true;
    geometry.computeVertexNormals();
    return geometry;
  };

  const createConstraintWallFromData = (constraintData) => {
    const wallGeometry = new THREE.BoxGeometry(0.2, 4, 2);
    const wallMaterial = new THREE.MeshLambertMaterial({
      color: new THREE.Color().setRGB(constraintData.color[0], constraintData.color[1], constraintData.color[2]),
      transparent: true,
      opacity: 0.6
    });
    const wall = new THREE.Mesh(wallGeometry, wallMaterial);
    
    wall.position.set(constraintData.position.x, constraintData.position.y, constraintData.position.z);
    wall.rotation.set(constraintData.rotation.x, constraintData.rotation.y, constraintData.rotation.z);
    wall.castShadow = true;
    
    return wall;
  };

  const createOptimalSolutionBeaconFromData = (optimalPointData) => {
    const beaconGeometry = new THREE.SphereGeometry(0.5, 16, 16);
    const beaconMaterial = new THREE.MeshLambertMaterial({
      color: new THREE.Color().setRGB(optimalPointData.color[0], optimalPointData.color[1], optimalPointData.color[2]),
      emissive: new THREE.Color().setRGB(optimalPointData.color[0], optimalPointData.color[1], optimalPointData.color[2]),
      emissiveIntensity: optimalPointData.intensity
    });
    const beacon = new THREE.Mesh(beaconGeometry, beaconMaterial);
    
    beacon.position.set(optimalPointData.position.x, optimalPointData.position.y, optimalPointData.position.z);
    beacon.castShadow = true;
    beacon.userData = { originalScale: 1, time: 0 };
    
    return beacon;
  };

  const createVariableNodeFromData = (variableData) => {
    const nodeGeometry = new THREE.SphereGeometry(0.3, 12, 12);
    const nodeMaterial = new THREE.MeshLambertMaterial({
      color: new THREE.Color().setRGB(variableData.color[0], variableData.color[1], variableData.color[2])
    });
    const node = new THREE.Mesh(nodeGeometry, nodeMaterial);
    
    node.position.set(variableData.position.x, variableData.position.y, variableData.position.z);
    node.castShadow = true;
    
    return node;
  };

  const createTerrainGeometry = (objectiveValue) => {
    const geometry = new THREE.PlaneGeometry(20, 20, 50, 50);
    const vertices = geometry.attributes.position.array;

    // Create terrain based on objective function
    for (let i = 0; i < vertices.length; i += 3) {
      const x = vertices[i];
      const y = vertices[i + 1];
      const z = Math.sin(x * 0.3) * Math.cos(y * 0.3) * 2 + 
                Math.sin(x * 0.1) * Math.cos(y * 0.1) * 1 +
                (objectiveValue / 1000) * 0.5;
      vertices[i + 2] = z;
    }

    geometry.attributes.position.needsUpdate = true;
    geometry.computeVertexNormals();
    return geometry;
  };

  const createConstraintWall = (constraint, index) => {
    const wallGeometry = new THREE.BoxGeometry(0.2, 4, 2);
    const wallMaterial = new THREE.MeshLambertMaterial({
      color: new THREE.Color().setHSL(index * 0.1, 0.7, 0.5),
      transparent: true,
      opacity: 0.6
    });
    const wall = new THREE.Mesh(wallGeometry, wallMaterial);
    
    // Position walls around the landscape
    const angle = (index / (result.model_building?.constraints?.length || 1)) * Math.PI * 2;
    wall.position.set(
      Math.cos(angle) * 8,
      2,
      Math.sin(angle) * 8
    );
    wall.rotation.y = angle;
    wall.castShadow = true;
    
    return wall;
  };

  const createOptimalSolutionBeacon = (solution) => {
    const beaconGeometry = new THREE.SphereGeometry(0.5, 16, 16);
    const beaconMaterial = new THREE.MeshLambertMaterial({
      color: 0xffd700,
      emissive: 0xffd700,
      emissiveIntensity: 0.5
    });
    const beacon = new THREE.Mesh(beaconGeometry, beaconMaterial);
    
    // Position at optimal point
    beacon.position.set(0, 3, 0);
    beacon.castShadow = true;

    // Add pulsing animation
    beacon.userData = { originalScale: 1, time: 0 };
    
    return beacon;
  };

  const createVariableNode = (variable, index) => {
    const nodeGeometry = new THREE.SphereGeometry(0.3, 12, 12);
    const nodeMaterial = new THREE.MeshLambertMaterial({
      color: new THREE.Color().setHSL(0.6 + index * 0.1, 0.8, 0.6)
    });
    const node = new THREE.Mesh(nodeGeometry, nodeMaterial);
    
    // Position nodes in a circle
    const angle = (index / (result.model_building?.variables?.length || 1)) * Math.PI * 2;
    node.position.set(
      Math.cos(angle) * 5,
      1,
      Math.sin(angle) * 5
    );
    node.castShadow = true;

    return node;
  };

  const createSolutionPath = (solution) => {
    const pathGeometry = new THREE.BufferGeometry();
    const points = [];
    
    // Create a spiral path to the optimal solution
    for (let i = 0; i < 100; i++) {
      const t = i / 100;
      const angle = t * Math.PI * 4;
      const radius = (1 - t) * 8;
      const height = t * 3;
      
      points.push(new THREE.Vector3(
        Math.cos(angle) * radius,
        height,
        Math.sin(angle) * radius
      ));
    }
    
    pathGeometry.setFromPoints(points);
    
    const pathMaterial = new THREE.LineBasicMaterial({
      color: 0x00ff00,
      linewidth: 2
    });
    
    const path = new THREE.Line(pathGeometry, pathMaterial);
    return path;
  };

  const createDataFlowParticles = (dataAnalysis) => {
    const particleCount = 100;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3;
      
      // Random positions
      positions[i3] = (Math.random() - 0.5) * 20;
      positions[i3 + 1] = Math.random() * 5;
      positions[i3 + 2] = (Math.random() - 0.5) * 20;
      
      // Blue to green gradient
      colors[i3] = 0.2 + Math.random() * 0.3; // R
      colors[i3 + 1] = 0.5 + Math.random() * 0.5; // G
      colors[i3 + 2] = 0.8 + Math.random() * 0.2; // B
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 0.1,
      vertexColors: true,
      transparent: true,
      opacity: 0.6
    });

    const particles = new THREE.Points(geometry, material);
    particles.userData = { time: 0 };
    
    return particles;
  };

  // Animation update
  useEffect(() => {
    if (!isLoaded || !sceneRef.current) return;

    const animate = () => {
      const scene = sceneRef.current;
      if (!scene) return;

      // Animate beacon pulsing
      const beacon = scene.getObjectByName('decisionLandscape')?.children.find(
        child => child.material?.emissiveIntensity !== undefined
      );
      if (beacon) {
        beacon.userData.time += 0.02;
        const scale = 1 + Math.sin(beacon.userData.time) * 0.2;
        beacon.scale.setScalar(scale);
      }

      // Animate particles
      const particles = scene.getObjectByName('decisionLandscape')?.children.find(
        child => child.type === 'Points'
      );
      if (particles) {
        particles.userData.time += 0.01;
        particles.rotation.y += 0.005;
        
        const positions = particles.geometry.attributes.position.array;
        for (let i = 0; i < positions.length; i += 3) {
          positions[i + 1] += Math.sin(particles.userData.time + i) * 0.01;
        }
        particles.geometry.attributes.position.needsUpdate = true;
      }
    };

    const interval = setInterval(animate, 16); // ~60fps
    return () => clearInterval(interval);
  }, [isLoaded]);

  return (
    <div className="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 rounded-2xl border border-gray-700 w-full max-w-6xl h-[90vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
              <BarChart3 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">3D Decision Landscape</h2>
              <p className="text-gray-400">Interactive mathematical optimization visualization</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors text-gray-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* 3D Viewport */}
        <div className="flex-1 relative">
          <div ref={mountRef} className="w-full h-full" />
          
          {/* Legend */}
          <div className="absolute top-4 left-4 bg-gray-800/90 backdrop-blur-sm rounded-lg p-4 border border-gray-600">
            <h3 className="text-white font-semibold mb-3">Legend</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-gray-300">Objective Function (Terrain)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <span className="text-gray-300">Optimal Solution (Beacon)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span className="text-gray-300">Variables (Nodes)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                <span className="text-gray-300">Constraints (Walls)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-cyan-500 rounded-full"></div>
                <span className="text-gray-300">Data Flow (Particles)</span>
              </div>
            </div>
          </div>

          {/* Controls Info */}
          <div className="absolute bottom-4 left-4 bg-gray-800/90 backdrop-blur-sm rounded-lg p-3 border border-gray-600">
            <div className="text-xs text-gray-400">
              <div>🖱️ Left: Rotate | 🖱️ Right: Pan | 🖱️ Scroll: Zoom</div>
            </div>
          </div>

          {/* Loading State */}
          {!isLoaded && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900/80">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                <p className="text-white">Loading 3D Visualization...</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DecisionLandscape3D;
