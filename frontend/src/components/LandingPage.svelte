<script lang="ts">
    import * as THREE from "three";
    import { onMount } from "svelte";
  
    let container: HTMLDivElement;
    let scene: THREE.Scene;
    let camera: THREE.PerspectiveCamera;
    let renderer: THREE.WebGLRenderer;
    let cube: THREE.Mesh;
  
    onMount(() => {
      scene = new THREE.Scene();
      camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
      camera.position.z = 3;
  
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setSize(window.innerWidth, window.innerHeight);
      container.appendChild(renderer.domElement);
  
      // Cube logo placeholder (replace with Mapster logo 3D object if you want)
      const geometry = new THREE.BoxGeometry();
      const material = new THREE.MeshStandardMaterial({ color: 0x60a5fa, metalness: 0.6, roughness: 0.2 });
      cube = new THREE.Mesh(geometry, material);
      scene.add(cube);
  
      const light = new THREE.PointLight(0xffffff, 1);
      light.position.set(5, 5, 5);
      scene.add(light);
  
      function animate() {
        requestAnimationFrame(animate);
        cube.rotation.x += 0.01;
        cube.rotation.y += 0.01;
        renderer.render(scene, camera);
      }
      animate();
  
      window.addEventListener("resize", () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      });
    });
  
    function launch() {
      window.location.href = "/map"; // or navigate programmatically
    }
  </script>
  
  <div bind:this={container} class="landing-bg"></div>
  
  <div class="landing-content">
    <h1 class="title">Mapster</h1>
    <button class="launch-btn" on:click={launch}>Launch Map</button>
  </div>
  
  <style>
    .landing-bg {
      position: absolute;
      width: 100%;
      height: 100%;
      overflow: hidden;
      top: 0;
      left: 0;
      z-index: 0;
    }
    .landing-content {
      position: relative;
      z-index: 10;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      text-align: center;
    }
    .title {
      font-size: 5rem;
      font-weight: 900;
      background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      text-shadow: 0 0 30px rgba(96,165,250,0.7);
      animation: glow 4s infinite alternate;
    }
    @keyframes glow {
      from { text-shadow: 0 0 20px rgba(96,165,250,0.6); }
      to { text-shadow: 0 0 40px rgba(167,139,250,0.9); }
    }
    .launch-btn {
      margin-top: 2rem;
      padding: 14px 28px;
      font-size: 1.2rem;
      font-weight: 600;
      border-radius: 999px;
      border: none;
      cursor: pointer;
      background: linear-gradient(90deg, #3b82f6, #9333ea);
      color: white;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .launch-btn:hover {
      transform: scale(1.05);
      box-shadow: 0 0 20px rgba(96,165,250,0.6), 0 0 40px rgba(147,51,234,0.6);
    }
  </style>
  