<script lang="ts">
    import * as THREE from "three";
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { tick } from "svelte";
  
    let container: HTMLDivElement;
    let scene: THREE.Scene;
    let camera: THREE.PerspectiveCamera;
    let renderer: THREE.WebGLRenderer;
    let particles: THREE.Points;
    let ring: THREE.Mesh;
    let expanded = false;
  
    onMount(() => {
      scene = new THREE.Scene();
      camera = new THREE.PerspectiveCamera(
        75,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
      );
      camera.position.z = 6;
  
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setSize(window.innerWidth, window.innerHeight);
      container.appendChild(renderer.domElement);
  
      // 🌌 Minimal particle field
      const particleGeometry = new THREE.BufferGeometry();
      const particleCount = 500;
      const positions = new Float32Array(particleCount * 3);
      for (let i = 0; i < particleCount * 3; i++) {
        positions[i] = (Math.random() - 0.5) * 20;
      }
      particleGeometry.setAttribute(
        "position",
        new THREE.BufferAttribute(positions, 3)
      );
      const particleMaterial = new THREE.PointsMaterial({
        color: 0xff0033,
        size: 0.04,
        transparent: true,
        opacity: 0.7
      });
      particles = new THREE.Points(particleGeometry, particleMaterial);
      scene.add(particles);
  
      // 🔴 Simple glowing ring
      const ringGeometry = new THREE.TorusGeometry(2.5, 0.05, 16, 100);
      const ringMaterial = new THREE.MeshBasicMaterial({
        color: 0xff0033,
        wireframe: true
      });
      ring = new THREE.Mesh(ringGeometry, ringMaterial);
      scene.add(ring);
  
      // Lights
      const ambient = new THREE.AmbientLight(0xffffff, 0.5);
      scene.add(ambient);
  
      // Animate
      function animate() {
        requestAnimationFrame(animate);
        particles.rotation.y += 0.0006;
        ring.rotation.z += 0.002;
        renderer.render(scene, camera);
      }
      animate();
    });
  
    async function launch() {
      expanded = true;
      await tick();
      setTimeout(() => goto("/map"), 1200);
    }
  </script>
  
  <svelte:head>
    <link
      href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&display=swap"
      rel="stylesheet"
    />
  </svelte:head>
  
  <div class="outer">
    <div class="frosted-frame {expanded ? 'expanded' : ''}">
      <div bind:this={container} class="landing-bg"></div>
  
      <div class="landing-content">
        <img src="/logo.svg" alt="Mapster Logo" class="logo" />
  
        <p class="description">Discover events. Explore differently.</p>
  
        <button class="launch-btn" on:click={launch}>Enter Map</button>
      </div>
    </div>
  </div>
  
  <style>
    .outer {
      position: absolute;
      inset: 0;
      display: flex;
      justify-content: center;
      align-items: center;
      background: black;
      overflow: hidden;
    }
  
    .frosted-frame {
      position: relative;
      width: 65vw;
      height: 65vh;
      border-radius: 20px;
      overflow: hidden;
      backdrop-filter: blur(12px) saturate(160%);
      background: rgba(0, 0, 0, 0.5);
      box-shadow: 0 0 30px rgba(255, 0, 51, 0.5);
      transition: all 1.2s ease;
    }
  
    .frosted-frame.expanded {
      width: 100vw;
      height: 100vh;
      border-radius: 0;
      box-shadow: none;
      backdrop-filter: blur(0);
      background: black;
    }
  
    .landing-bg {
      position: absolute;
      width: 100%;
      height: 100%;
      z-index: 0;
    }
  
    .landing-content {
      position: relative;
      z-index: 10;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      text-align: center;
    }
  
    .logo {
      width: 220px;
      filter: drop-shadow(0 0 35px rgba(255, 0, 51, 0.9));
      animation: pulse 3s infinite ease-in-out;
      margin-bottom: 1.2rem;
    }
  
    .description {
      font-size: 1.1rem;
      font-family: "Orbitron", sans-serif;
      color: #f1f1f1;
      margin-bottom: 2rem;
      letter-spacing: 1px;
      text-shadow: 0 0 12px rgba(255, 0, 51, 0.6);
    }
  
    .launch-btn {
      padding: 12px 32px;
      font-size: 1.2rem;
      font-family: "Orbitron", sans-serif;
      font-weight: 700;
      border-radius: 50px;
      border: 2px solid #ff0033;
      background: black;
      color: #ff0033;
      cursor: pointer;
      transition: all 0.3s ease;
    }
  
    .launch-btn:hover {
      color: white;
      background: #ff0033;
      box-shadow: 0 0 20px rgba(255, 0, 51, 0.8);
      transform: scale(1.05);
    }
  
    @keyframes pulse {
      0% {
        transform: scale(1);
        filter: drop-shadow(0 0 20px rgba(255, 0, 51, 0.7));
      }
      50% {
        transform: scale(1.04);
        filter: drop-shadow(0 0 45px rgba(255, 0, 51, 1));
      }
      100% {
        transform: scale(1);
        filter: drop-shadow(0 0 20px rgba(255, 0, 51, 0.7));
      }
    }
  </style>
  