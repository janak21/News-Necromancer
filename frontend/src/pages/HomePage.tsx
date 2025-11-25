import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout, Card, Button, Grid, Flex } from '../components';
import { useGhostNotificationContext } from '../contexts/GhostNotificationContext';
import useTheme from '../hooks/useTheme';
import './HomePage.css';

const HomePage: React.FC = () => {
  const { colors } = useTheme();
  const { showSuccess, showError, showWarning, showInfo } = useGhostNotificationContext();
  const navigate = useNavigate();

  const handleStartSpooking = () => {
    showInfo("🎭 Summoning the spooky feeds portal...");
    setTimeout(() => {
      navigate('/feeds');
    }, 1000);
  };

  const handleViewExamples = () => {
    showSuccess("👻 Manifesting cursed examples from the ethereal realm...");
    // Scroll to the demo section
    const demoSection = document.querySelector('.demo-section');
    if (demoSection) {
      demoSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleLearnMore = () => {
    showWarning("🔮 The ancient knowledge beckons... redirecting to preferences...");
    setTimeout(() => {
      navigate('/preferences');
    }, 1500);
  };

  const spookyFacts = [
    "👻 Our AI has transformed over 10,000 mundane articles into spine-chilling tales",
    "🎭 5 different horror genres available: Gothic, Cosmic, Psychological, Folk, and Supernatural",
    "⚡ Process 100+ RSS feeds per minute with concurrent haunting technology",
    "🌙 Personalized horror intensity from gentle whispers to absolute terror",
    "🔮 Advanced content caching ensures your nightmares load instantly"
  ];

  const [currentFactIndex, setCurrentFactIndex] = React.useState(0);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setCurrentFactIndex((prev) => (prev + 1) % spookyFacts.length);
    }, 4000);
    return () => clearInterval(interval);
  }, [spookyFacts.length]);

  return (
    <Layout variant="container" maxWidth="lg" padding="md">
      <Flex direction="column" align="center" gap="lg">
        {/* Hero Section - Compact */}
        <div className="homepage-hero" style={{ textAlign: 'center', marginBottom: '1rem', paddingTop: '1rem' }}>
          <h1 style={{ 
            fontSize: 'clamp(2rem, 5vw, 3rem)', 
            fontWeight: 'var(--font-weight-bold)',
            marginBottom: 'var(--spacing-sm)',
            background: 'linear-gradient(45deg, var(--color-primary), var(--color-accent))',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            lineHeight: 1.2
          }}>
            🎃 Spooky RSS System
          </h1>
          <p style={{ 
            fontSize: 'clamp(1rem, 2vw, 1.125rem)', 
            color: colors.textSecondary,
            maxWidth: '600px',
            margin: '0 auto',
            lineHeight: 1.4
          }}>
            Transform your RSS feeds into spine-chilling horror stories with AI-powered spooky remixing!
          </p>
        </div>

        {/* Action Buttons - Moved Up */}
        <Flex gap="md" wrap className="action-buttons" style={{ marginTop: '0.5rem' }}>
          <Button variant="primary" size="lg" onClick={handleStartSpooking}>
            Start Spooking Feeds
          </Button>
          <Button variant="secondary" size="lg" onClick={handleViewExamples}>
            View Examples
          </Button>
          <Button variant="ghost" size="lg" onClick={handleLearnMore}>
            Learn More
          </Button>
        </Flex>

        {/* Feature Cards - Compact */}
        <Grid cols={3} gap="md" responsive style={{ width: '100%' }}>
          <Card variant="elevated" hover glow className="feature-card feature-card--compact">
            <div className="spooky-card__header">
              <h2 className="spooky-card__title" style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>👻 Horror Transformation</h2>
            </div>
            <div className="spooky-card__body">
              <p style={{ fontSize: '0.875rem', lineHeight: 1.4 }}>Convert ordinary RSS content into terrifying tales using advanced AI.</p>
            </div>
          </Card>

          <Card variant="elevated" hover glow className="feature-card feature-card--compact">
            <div className="spooky-card__header">
              <h2 className="spooky-card__title" style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>⚡ Lightning Fast</h2>
            </div>
            <div className="spooky-card__body">
              <p style={{ fontSize: '0.875rem', lineHeight: 1.4 }}>Process 100+ RSS feeds per minute with concurrent fetching.</p>
            </div>
          </Card>

          <Card variant="elevated" hover glow className="feature-card feature-card--compact">
            <div className="spooky-card__header">
              <h2 className="spooky-card__title" style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>🎨 Personalized</h2>
            </div>
            <div className="spooky-card__body">
              <p style={{ fontSize: '0.875rem', lineHeight: 1.4 }}>Customize horror intensity and themes to match your preferences.</p>
            </div>
          </Card>
        </Grid>

        {/* Rotating Spooky Facts - Compact */}
        <Card variant="ghost" padding="sm" className="rotating-facts" style={{ 
          width: '100%', 
          maxWidth: '600px', 
          textAlign: 'center',
          minHeight: '60px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <p style={{ 
            color: colors.primary, 
            fontSize: 'clamp(0.875rem, 1.5vw, 1rem)',
            fontStyle: 'italic',
            margin: 0,
            transition: 'opacity 0.5s ease-in-out',
            lineHeight: 1.4
          }}>
            {spookyFacts[currentFactIndex]}
          </p>
        </Card>

        {/* Ghost Notification Demo - Compact */}
        <Card variant="outlined" padding="sm" style={{ width: '100%', maxWidth: '600px' }}>
          <div className="spooky-card__header">
            <h2 className="spooky-card__title" style={{ fontSize: '1rem', marginBottom: '0.25rem' }}>👻 Test Ghost Notifications</h2>
            <p style={{ color: colors.textSecondary, fontSize: '0.875rem', marginBottom: '0.5rem' }}>
              Try out the spooky notification system
            </p>
          </div>
          <Flex gap="sm" wrap>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => { showSuccess("🎉 Spooky transformation complete!"); }}
            >
              Success
            </Button>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => { showError("💀 Something went terribly wrong..."); }}
            >
              Error
            </Button>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => { showWarning("⚠️ The spirits are restless tonight..."); }}
            >
              Warning
            </Button>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => { showInfo("🔮 New spooky content available!"); }}
            >
              Info
            </Button>
          </Flex>
        </Card>

        {/* Demo Section */}
        <Card variant="outlined" padding="lg" style={{ width: '100%', maxWidth: '800px' }} className="demo-section demo-examples">
          <div className="spooky-card__header">
            <h2 className="spooky-card__title">🔮 See the Magic in Action</h2>
            <p className="spooky-card__subtitle">Watch how ordinary news becomes extraordinary horror</p>
          </div>
          <div className="spooky-card__body">
            <Grid cols={2} gap="md" responsive>
              <div>
                <h3 style={{ color: colors.textSecondary, marginBottom: 'var(--spacing-sm)' }}>
                  📰 Original RSS Content:
                </h3>
                <Card variant="ghost" padding="sm" style={{ marginBottom: 'var(--spacing-md)' }}>
                  <p style={{ fontStyle: 'italic', color: colors.textSecondary, fontSize: 'var(--font-size-sm)' }}>
                    "Local bakery opens new location downtown, featuring artisanal breads and pastries made with traditional recipes..."
                  </p>
                </Card>
                <Card variant="ghost" padding="sm" style={{ marginBottom: 'var(--spacing-md)' }}>
                  <p style={{ fontStyle: 'italic', color: colors.textSecondary, fontSize: 'var(--font-size-sm)' }}>
                    "City council approves new park construction project, expected to be completed by next summer..."
                  </p>
                </Card>
                <Card variant="ghost" padding="sm">
                  <p style={{ fontStyle: 'italic', color: colors.textSecondary, fontSize: 'var(--font-size-sm)' }}>
                    "Tech startup raises $2M in funding to develop innovative mobile app for food delivery..."
                  </p>
                </Card>
              </div>
              <div>
                <h3 style={{ color: colors.primary, marginBottom: 'var(--spacing-sm)' }}>
                  👻 Spooky Transformation:
                </h3>
                <Card variant="ghost" padding="sm" style={{ marginBottom: 'var(--spacing-md)' }}>
                  <p style={{ fontStyle: 'italic', color: colors.text, fontSize: 'var(--font-size-sm)' }}>
                    "Ancient bakery emerges from shadows downtown, where bread rises with whispered incantations and pastries hold secrets of the damned. The 'traditional recipes' are carved in bone..."
                  </p>
                </Card>
                <Card variant="ghost" padding="sm" style={{ marginBottom: 'var(--spacing-md)' }}>
                  <p style={{ fontStyle: 'italic', color: colors.text, fontSize: 'var(--font-size-sm)' }}>
                    "City council summons cursed grounds for ritual construction, where restless spirits will wander eternally among twisted trees that bleed sap under the blood moon..."
                  </p>
                </Card>
                <Card variant="ghost" padding="sm">
                  <p style={{ fontStyle: 'italic', color: colors.text, fontSize: 'var(--font-size-sm)' }}>
                    "Occult startup channels $2M from otherworldly investors to manifest haunted app that delivers souls instead of sustenance, trapping users in digital purgatory..."
                  </p>
                </Card>
              </div>
            </Grid>
            
            <div style={{ marginTop: 'var(--spacing-lg)', textAlign: 'center' }}>
              <p style={{ color: colors.textSecondary, fontStyle: 'italic' }}>
                ✨ Each transformation maintains the original meaning while adding layers of supernatural dread and atmospheric horror
              </p>
            </div>
          </div>
        </Card>
      </Flex>
    </Layout>
  );
};

export default HomePage;