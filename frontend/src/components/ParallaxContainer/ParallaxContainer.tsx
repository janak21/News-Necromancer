import React, { useEffect, useRef, useState } from 'react';
import './ParallaxContainer.css';

export type ParticleType = 'bats' | 'fog' | 'spirits';

export interface ParallaxContainerProps {
  children: React.ReactNode;
  particleTypes?: ParticleType[];
  particleDensity?: 'low' | 'medium' | 'high';
  enableParallax?: boolean;
  className?: string;
}

interface Particle {
  id: string;
  type: ParticleType;
  x: number;
  y: number;
  size: number;
  speed: number;
  parallaxFactor: number;
  rotation: number;
  opacity: number;
}

const ParallaxContainer: React.FC<ParallaxContainerProps> = ({
  children,
  particleTypes = ['bats', 'fog', 'spirits'],
  particleDensity = 'medium',
  enableParallax = true,
  className = ''
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const animationFrameRef = useRef<number | undefined>(undefined);
  const [scrollY, setScrollY] = useState(0);

  const densityMap = {
    low: 15,
    medium: 30,
    high: 50
  };

  const particleCount = densityMap[particleDensity];

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Initialize particles
    const initParticles = () => {
      particlesRef.current = [];
      
      particleTypes.forEach(type => {
        const count = Math.floor(particleCount / particleTypes.length);
        
        for (let i = 0; i < count; i++) {
          particlesRef.current.push({
            id: `${type}-${i}`,
            type,
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            size: getParticleSize(type),
            speed: getParticleSpeed(type),
            parallaxFactor: getParallaxFactor(type),
            rotation: Math.random() * Math.PI * 2,
            opacity: getParticleOpacity(type)
          });
        }
      });
    };

    initParticles();

    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particlesRef.current.forEach(particle => {
        // Update position with parallax effect
        const parallaxOffset = enableParallax ? scrollY * particle.parallaxFactor : 0;
        
        particle.x += Math.cos(particle.rotation) * particle.speed;
        particle.y += Math.sin(particle.rotation) * particle.speed - parallaxOffset * 0.01;

        // Wrap around edges
        if (particle.x < -50) particle.x = canvas.width + 50;
        if (particle.x > canvas.width + 50) particle.x = -50;
        if (particle.y < -50) particle.y = canvas.height + 50;
        if (particle.y > canvas.height + 50) particle.y = -50;

        // Slight rotation change for organic movement
        particle.rotation += (Math.random() - 0.5) * 0.02;

        // Draw particle
        drawParticle(ctx, particle);
      });

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      window.removeEventListener('resize', resizeCanvas);
    };
  }, [particleTypes, particleCount, scrollY, enableParallax]);

  const getParticleSize = (type: ParticleType): number => {
    switch (type) {
      case 'bats':
        return Math.random() * 15 + 10;
      case 'fog':
        return Math.random() * 80 + 60;
      case 'spirits':
        return Math.random() * 25 + 15;
      default:
        return 10;
    }
  };

  const getParticleSpeed = (type: ParticleType): number => {
    switch (type) {
      case 'bats':
        return Math.random() * 1.5 + 0.8;
      case 'fog':
        return Math.random() * 0.3 + 0.1;
      case 'spirits':
        return Math.random() * 0.6 + 0.3;
      default:
        return 0.5;
    }
  };

  const getParallaxFactor = (type: ParticleType): number => {
    switch (type) {
      case 'bats':
        return 0.3;
      case 'fog':
        return 0.1;
      case 'spirits':
        return 0.2;
      default:
        return 0.2;
    }
  };

  const getParticleOpacity = (type: ParticleType): number => {
    switch (type) {
      case 'bats':
        return Math.random() * 0.4 + 0.3;
      case 'fog':
        return Math.random() * 0.15 + 0.05;
      case 'spirits':
        return Math.random() * 0.3 + 0.2;
      default:
        return 0.3;
    }
  };

  const drawParticle = (ctx: CanvasRenderingContext2D, particle: Particle) => {
    ctx.save();
    ctx.globalAlpha = particle.opacity;
    ctx.translate(particle.x, particle.y);
    ctx.rotate(particle.rotation);

    switch (particle.type) {
      case 'bats':
        drawBat(ctx, particle.size);
        break;
      case 'fog':
        drawFog(ctx, particle.size);
        break;
      case 'spirits':
        drawSpirit(ctx, particle.size);
        break;
    }

    ctx.restore();
  };

  const drawBat = (ctx: CanvasRenderingContext2D, size: number) => {
    ctx.fillStyle = '#8b5cf6';
    ctx.beginPath();
    // Left wing
    ctx.moveTo(-size / 2, 0);
    ctx.quadraticCurveTo(-size, -size / 3, -size / 2, -size / 2);
    // Body
    ctx.lineTo(0, 0);
    // Right wing
    ctx.lineTo(size / 2, -size / 2);
    ctx.quadraticCurveTo(size, -size / 3, size / 2, 0);
    ctx.closePath();
    ctx.fill();
  };

  const drawFog = (ctx: CanvasRenderingContext2D, size: number) => {
    const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, size / 2);
    gradient.addColorStop(0, 'rgba(139, 92, 246, 0.3)');
    gradient.addColorStop(0.5, 'rgba(139, 92, 246, 0.1)');
    gradient.addColorStop(1, 'rgba(139, 92, 246, 0)');
    
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(0, 0, size / 2, 0, Math.PI * 2);
    ctx.fill();
  };

  const drawSpirit = (ctx: CanvasRenderingContext2D, size: number) => {
    const gradient = ctx.createLinearGradient(0, -size / 2, 0, size / 2);
    gradient.addColorStop(0, 'rgba(139, 92, 246, 0.5)');
    gradient.addColorStop(0.5, 'rgba(167, 139, 250, 0.3)');
    gradient.addColorStop(1, 'rgba(139, 92, 246, 0)');
    
    ctx.fillStyle = gradient;
    ctx.beginPath();
    // Ghostly wisp shape
    ctx.ellipse(0, -size / 4, size / 3, size / 2, 0, 0, Math.PI * 2);
    ctx.fill();
    
    // Tail
    ctx.beginPath();
    ctx.moveTo(0, size / 4);
    ctx.quadraticCurveTo(-size / 4, size / 2, 0, size);
    ctx.quadraticCurveTo(size / 4, size / 2, 0, size / 4);
    ctx.fill();
  };

  return (
    <div ref={containerRef} className={`parallax-container ${className}`}>
      <canvas
        ref={canvasRef}
        className="parallax-container__canvas"
      />
      
      <div className="parallax-container__content">
        {children}
      </div>
    </div>
  );
};

export default ParallaxContainer;
