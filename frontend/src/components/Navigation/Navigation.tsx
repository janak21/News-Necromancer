import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Ghost, Rss, Settings } from 'lucide-react';
import { useSoundEffects } from '../../hooks';
import './Navigation.css';

const Navigation: React.FC = () => {
  const location = useLocation();
  const { playSound } = useSoundEffects();

  const navItems = [
    { path: '/', label: 'Home', icon: Ghost },
    { path: '/feeds', label: 'Spooky Feeds', icon: Rss },
    { path: '/preferences', label: 'Preferences', icon: Settings },
  ];

  const handleNavClick = () => {
    playSound('creak');
  };

  return (
    <nav className="navigation">
      <div className="nav-brand">
        <Ghost className="brand-icon" />
        <span className="brand-text">Spooky RSS</span>
      </div>
      <ul className="nav-links">
        {navItems.map(({ path, label, icon: Icon }) => (
          <li key={path}>
            <Link
              to={path}
              className={`nav-link ${location.pathname === path ? 'active' : ''}`}
              onClick={handleNavClick}
            >
              <Icon size={18} />
              <span>{label}</span>
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Navigation;