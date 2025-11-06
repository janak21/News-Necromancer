"""
Personalization Engine for horror content customization
"""

from typing import Dict, Any, Optional, List
import logging

from ..models.data_models import UserPreferences, HorrorType


class PersonalizationEngine:
    """Applies user personalization to horror content"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Intensity level adjustments
        self.intensity_adjustments = {
            1: {
                "title_modifiers": ["mysterious", "strange", "unusual"],
                "summary_tone": "subtle and atmospheric",
                "horror_reduction": 0.8
            },
            2: {
                "title_modifiers": ["unsettling", "eerie", "disturbing"],
                "summary_tone": "mildly unsettling",
                "horror_reduction": 0.6
            },
            3: {
                "title_modifiers": ["frightening", "terrifying", "haunting"],
                "summary_tone": "moderately scary",
                "horror_reduction": 0.4
            },
            4: {
                "title_modifiers": ["horrifying", "nightmarish", "dreadful"],
                "summary_tone": "quite frightening",
                "horror_reduction": 0.2
            },
            5: {
                "title_modifiers": ["apocalyptic", "soul-crushing", "mind-shattering"],
                "summary_tone": "intensely terrifying",
                "horror_reduction": 0.0
            }
        }
        
        # Horror type specific language patterns
        self.horror_type_language = {
            HorrorType.GOTHIC: {
                "descriptors": ["ancient", "crumbling", "shadowy", "foreboding"],
                "settings": ["mansion", "cathedral", "cemetery", "castle"],
                "atmosphere": "brooding and atmospheric"
            },
            HorrorType.PSYCHOLOGICAL: {
                "descriptors": ["twisted", "distorted", "fragmented", "unstable"],
                "settings": ["mind", "reality", "perception", "consciousness"],
                "atmosphere": "unsettling and mind-bending"
            },
            HorrorType.COSMIC: {
                "descriptors": ["incomprehensible", "vast", "alien", "otherworldly"],
                "settings": ["void", "dimension", "cosmos", "reality"],
                "atmosphere": "existentially terrifying"
            },
            HorrorType.FOLK: {
                "descriptors": ["ancient", "traditional", "rural", "primitive"],
                "settings": ["forest", "village", "countryside", "ritual site"],
                "atmosphere": "primal and earthy"
            },
            HorrorType.SUPERNATURAL: {
                "descriptors": ["spectral", "ethereal", "ghostly", "spiritual"],
                "settings": ["haunted house", "graveyard", "séance room", "spirit realm"],
                "atmosphere": "otherworldly and haunting"
            }
        }
    
    def apply_personalization(self, content: Dict[str, Any], preferences: UserPreferences) -> Dict[str, Any]:
        """
        Apply user personalization to horror content
        
        Args:
            content: Original horror content dictionary
            preferences: User preferences
            
        Returns:
            Personalized content dictionary
        """
        try:
            personalized_content = content.copy()
            
            # Apply intensity adjustments
            personalized_content = self._apply_intensity_adjustment(
                personalized_content, preferences.intensity_level
            )
            
            # Apply horror type preferences
            if preferences.preferred_horror_types:
                personalized_content = self._apply_horror_type_preferences(
                    personalized_content, preferences.preferred_horror_types
                )
            
            # Apply content filters
            if preferences.content_filters:
                personalized_content = self._apply_content_filters(
                    personalized_content, preferences.content_filters
                )
            
            return personalized_content
            
        except Exception as e:
            self.logger.error(f"Error applying personalization: {str(e)}")
            return content  # Return original content if personalization fails
    
    def _apply_intensity_adjustment(self, content: Dict[str, Any], intensity_level: int) -> Dict[str, Any]:
        """
        Adjust content intensity based on user preference
        
        Args:
            content: Content to adjust
            intensity_level: Desired intensity level (1-5)
            
        Returns:
            Intensity-adjusted content
        """
        if intensity_level not in self.intensity_adjustments:
            return content
        
        adjustments = self.intensity_adjustments[intensity_level]
        adjusted_content = content.copy()
        
        # Adjust title intensity
        title = adjusted_content.get("haunted_title", "")
        if intensity_level <= 2:
            # Tone down extreme language for lower intensities
            extreme_words = ["terrifying", "horrifying", "nightmarish", "apocalyptic"]
            for word in extreme_words:
                if word in title.lower():
                    modifier = adjustments["title_modifiers"][0]
                    title = title.replace(word, modifier)
            adjusted_content["haunted_title"] = title
        
        # Adjust summary intensity
        summary = adjusted_content.get("haunted_summary", "")
        if intensity_level <= 2:
            # Replace intense language with milder alternatives
            intense_phrases = {
                "soul-crushing": "unsettling",
                "mind-shattering": "disturbing",
                "bone-chilling": "eerie",
                "blood-curdling": "unsettling",
                "spine-tingling": "mysterious"
            }
            for intense, mild in intense_phrases.items():
                summary = summary.replace(intense, mild)
            adjusted_content["haunted_summary"] = summary
        
        return adjusted_content
    
    def _apply_horror_type_preferences(self, content: Dict[str, Any], preferred_types: List[HorrorType]) -> Dict[str, Any]:
        """
        Apply horror type preferences to content
        
        Args:
            content: Content to modify
            preferred_types: List of preferred horror types
            
        Returns:
            Content adjusted for horror type preferences
        """
        if not preferred_types:
            return content
        
        adjusted_content = content.copy()
        primary_type = preferred_types[0]  # Use first preference as primary
        
        if primary_type in self.horror_type_language:
            type_language = self.horror_type_language[primary_type]
            
            # Enhance themes with type-specific elements
            themes = adjusted_content.get("horror_themes", [])
            
            # Add type-specific descriptors to themes
            enhanced_themes = []
            for theme in themes:
                # Add descriptors that match the horror type
                for descriptor in type_language["descriptors"][:2]:
                    if descriptor not in theme:
                        enhanced_theme = f"{descriptor} {theme}"
                        enhanced_themes.append(enhanced_theme)
                        break
                else:
                    enhanced_themes.append(theme)
            
            adjusted_content["horror_themes"] = enhanced_themes
            
            # Enhance supernatural explanation with type-specific atmosphere
            explanation = adjusted_content.get("supernatural_explanation", "")
            atmosphere = type_language["atmosphere"]
            if explanation and atmosphere not in explanation:
                explanation += f" The atmosphere is {atmosphere}."
                adjusted_content["supernatural_explanation"] = explanation
        
        return adjusted_content
    
    def _apply_content_filters(self, content: Dict[str, Any], content_filters: List[str]) -> Dict[str, Any]:
        """
        Apply content filters to remove unwanted elements
        
        Args:
            content: Content to filter
            content_filters: List of terms/themes to filter out
            
        Returns:
            Filtered content
        """
        if not content_filters:
            return content
        
        filtered_content = content.copy()
        
        # Filter horror themes
        themes = filtered_content.get("horror_themes", [])
        filtered_themes = []
        
        for theme in themes:
            should_filter = False
            for filter_term in content_filters:
                if filter_term.lower() in theme.lower():
                    should_filter = True
                    break
            
            if not should_filter:
                filtered_themes.append(theme)
        
        filtered_content["horror_themes"] = filtered_themes
        
        # Filter content from title and summary
        for field in ["haunted_title", "haunted_summary", "supernatural_explanation"]:
            text = filtered_content.get(field, "")
            for filter_term in content_filters:
                # Replace filtered terms with milder alternatives
                if filter_term.lower() in text.lower():
                    text = text.replace(filter_term, "mysterious")
            filtered_content[field] = text
        
        return filtered_content
    
    def create_personalized_prompt_additions(self, preferences: UserPreferences) -> str:
        """
        Create additional prompt text based on user preferences
        
        Args:
            preferences: User preferences
            
        Returns:
            Additional prompt text for LLM
        """
        additions = []
        
        # Add intensity guidance
        if preferences.intensity_level:
            intensity_guidance = self.intensity_adjustments.get(preferences.intensity_level, {})
            tone = intensity_guidance.get("summary_tone", "moderately scary")
            additions.append(f"Make the horror {tone}.")
        
        # Add horror type guidance
        if preferences.preferred_horror_types:
            type_names = [ht.value for ht in preferences.preferred_horror_types]
            additions.append(f"Focus on {', '.join(type_names)} horror elements.")
        
        # Add content filter guidance
        if preferences.content_filters:
            additions.append(f"Avoid these elements: {', '.join(preferences.content_filters)}.")
        
        return " ".join(additions)
    
    def validate_personalized_content(self, content: Dict[str, Any], preferences: UserPreferences) -> bool:
        """
        Validate that personalized content meets user preferences
        
        Args:
            content: Content to validate
            preferences: User preferences to validate against
            
        Returns:
            True if content meets preferences, False otherwise
        """
        try:
            # Check content filters
            if preferences.content_filters:
                for field in ["haunted_title", "haunted_summary", "supernatural_explanation"]:
                    text = content.get(field, "").lower()
                    for filter_term in preferences.content_filters:
                        if filter_term.lower() in text:
                            return False
            
            # Check horror themes
            themes = content.get("horror_themes", [])
            if preferences.content_filters:
                for theme in themes:
                    for filter_term in preferences.content_filters:
                        if filter_term.lower() in theme.lower():
                            return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating personalized content: {str(e)}")
            return True  # Default to valid if validation fails
    
    def create_user_profile(self, user_id: str, initial_preferences: Optional[Dict[str, Any]] = None) -> UserPreferences:
        """
        Create a new user profile with default or specified preferences
        
        Args:
            user_id: Unique user identifier
            initial_preferences: Optional initial preferences
            
        Returns:
            UserPreferences object
        """
        from ..models.data_models import UserPreferences, HorrorType
        
        if initial_preferences:
            preferences = UserPreferences.from_dict(initial_preferences)
            preferences.user_id = user_id
        else:
            # Create default preferences
            preferences = UserPreferences(
                user_id=user_id,
                preferred_horror_types=[HorrorType.SUPERNATURAL, HorrorType.GOTHIC],
                intensity_level=3,
                content_filters=[],
                notification_settings={
                    "ghost_notifications": True,
                    "new_variants": True,
                    "processing_complete": True,
                    "error_alerts": False
                },
                theme_customizations={
                    "primary_color": "#1a1a1a",
                    "accent_color": "#8b0000",
                    "font_family": "serif"
                }
            )
        
        return preferences
    
    def analyze_user_engagement(self, user_preferences: UserPreferences, content_interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze user engagement to suggest preference improvements
        
        Args:
            user_preferences: Current user preferences
            content_interactions: List of user interactions with content
            
        Returns:
            Analysis results and suggestions
        """
        analysis = {
            "engagement_score": 0.0,
            "preferred_themes": [],
            "suggested_intensity": user_preferences.intensity_level,
            "suggested_horror_types": user_preferences.preferred_horror_types,
            "recommendations": []
        }
        
        if not content_interactions:
            return analysis
        
        # Analyze theme preferences from interactions
        theme_scores = {}
        total_interactions = len(content_interactions)
        
        for interaction in content_interactions:
            themes = interaction.get("horror_themes", [])
            engagement = interaction.get("engagement_score", 0)  # likes, shares, time spent
            
            for theme in themes:
                if theme not in theme_scores:
                    theme_scores[theme] = []
                theme_scores[theme].append(engagement)
        
        # Calculate average engagement per theme
        avg_theme_scores = {}
        for theme, scores in theme_scores.items():
            avg_theme_scores[theme] = sum(scores) / len(scores)
        
        # Sort themes by engagement
        sorted_themes = sorted(avg_theme_scores.items(), key=lambda x: x[1], reverse=True)
        analysis["preferred_themes"] = [theme for theme, score in sorted_themes[:5]]
        
        # Calculate overall engagement score
        all_scores = [interaction.get("engagement_score", 0) for interaction in content_interactions]
        analysis["engagement_score"] = sum(all_scores) / len(all_scores) if all_scores else 0
        
        # Generate recommendations
        if analysis["engagement_score"] < 0.3:
            analysis["recommendations"].append("Consider adjusting intensity level or horror types")
        
        if len(analysis["preferred_themes"]) > 0:
            top_theme = analysis["preferred_themes"][0]
            analysis["recommendations"].append(f"Focus more on '{top_theme}' themes")
        
        return analysis
    
    def optimize_preferences_for_user(self, user_preferences: UserPreferences, engagement_analysis: Dict[str, Any]) -> UserPreferences:
        """
        Optimize user preferences based on engagement analysis
        
        Args:
            user_preferences: Current preferences
            engagement_analysis: Results from analyze_user_engagement
            
        Returns:
            Optimized UserPreferences
        """
        optimized = user_preferences.to_dict()
        
        # Adjust intensity based on engagement
        engagement_score = engagement_analysis.get("engagement_score", 0)
        if engagement_score < 0.3 and user_preferences.intensity_level > 1:
            optimized["intensity_level"] = max(1, user_preferences.intensity_level - 1)
        elif engagement_score > 0.7 and user_preferences.intensity_level < 5:
            optimized["intensity_level"] = min(5, user_preferences.intensity_level + 1)
        
        # Update preferred themes based on engagement
        preferred_themes = engagement_analysis.get("preferred_themes", [])
        if preferred_themes:
            # Map themes to horror types
            from .horror_themes import HorrorThemeManager
            theme_manager = HorrorThemeManager()
            
            suggested_types = set()
            for theme in preferred_themes[:3]:  # Top 3 themes
                horror_type = theme_manager.categorize_theme(theme)
                if horror_type:
                    suggested_types.add(horror_type)
            
            if suggested_types:
                optimized["preferred_horror_types"] = list(suggested_types)
        
        return UserPreferences.from_dict(optimized)


class ContentCustomizationAlgorithm:
    """Advanced algorithms for content filtering and customization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Content quality thresholds
        self.quality_thresholds = {
            "min_horror_themes": 2,
            "max_horror_themes": 8,
            "min_summary_length": 100,
            "max_summary_length": 500,
            "min_title_length": 10,
            "max_title_length": 100
        }
        
        # Sentiment analysis for horror intensity
        self.horror_intensity_keywords = {
            1: ["mysterious", "strange", "unusual", "odd"],
            2: ["unsettling", "eerie", "disturbing", "ominous"],
            3: ["frightening", "terrifying", "haunting", "sinister"],
            4: ["horrifying", "nightmarish", "dreadful", "ghastly"],
            5: ["apocalyptic", "soul-crushing", "mind-shattering", "utterly terrifying"]
        }
    
    def filter_content_by_quality(self, variants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter content variants based on quality metrics
        
        Args:
            variants: List of content variants to filter
            
        Returns:
            Filtered list of high-quality variants
        """
        filtered_variants = []
        
        for variant in variants:
            if self._meets_quality_standards(variant):
                filtered_variants.append(variant)
        
        # Sort by quality score
        filtered_variants.sort(key=self._calculate_quality_score, reverse=True)
        
        return filtered_variants
    
    def _meets_quality_standards(self, variant: Dict[str, Any]) -> bool:
        """
        Check if a variant meets quality standards
        
        Args:
            variant: Content variant to check
            
        Returns:
            True if meets standards, False otherwise
        """
        try:
            # Check horror themes count
            themes = variant.get("horror_themes", [])
            if not (self.quality_thresholds["min_horror_themes"] <= 
                   len(themes) <= self.quality_thresholds["max_horror_themes"]):
                return False
            
            # Check summary length
            summary = variant.get("haunted_summary", "")
            if not (self.quality_thresholds["min_summary_length"] <= 
                   len(summary) <= self.quality_thresholds["max_summary_length"]):
                return False
            
            # Check title length
            title = variant.get("haunted_title", "")
            if not (self.quality_thresholds["min_title_length"] <= 
                   len(title) <= self.quality_thresholds["max_title_length"]):
                return False
            
            # Check for supernatural explanation
            explanation = variant.get("supernatural_explanation", "")
            if len(explanation) < 20:  # Minimum explanation length
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking quality standards: {str(e)}")
            return False
    
    def _calculate_quality_score(self, variant: Dict[str, Any]) -> float:
        """
        Calculate quality score for a variant
        
        Args:
            variant: Content variant to score
            
        Returns:
            Quality score (0.0 to 1.0)
        """
        score = 0.0
        
        try:
            # Theme diversity score (0.2 weight)
            themes = variant.get("horror_themes", [])
            theme_score = min(len(themes) / 5.0, 1.0) * 0.2
            score += theme_score
            
            # Content length score (0.2 weight)
            summary = variant.get("haunted_summary", "")
            optimal_length = 250
            length_score = 1.0 - abs(len(summary) - optimal_length) / optimal_length
            length_score = max(0, min(1.0, length_score)) * 0.2
            score += length_score
            
            # Horror intensity consistency (0.3 weight)
            intensity_score = self._calculate_intensity_consistency(variant) * 0.3
            score += intensity_score
            
            # Creativity score (0.3 weight)
            creativity_score = self._calculate_creativity_score(variant) * 0.3
            score += creativity_score
            
        except Exception as e:
            self.logger.error(f"Error calculating quality score: {str(e)}")
            return 0.0
        
        return min(1.0, score)
    
    def _calculate_intensity_consistency(self, variant: Dict[str, Any]) -> float:
        """
        Calculate how consistent the horror intensity is across the variant
        
        Args:
            variant: Content variant to analyze
            
        Returns:
            Consistency score (0.0 to 1.0)
        """
        try:
            title = variant.get("haunted_title", "").lower()
            summary = variant.get("haunted_summary", "").lower()
            
            # Count intensity keywords in title and summary
            title_intensity = 0
            summary_intensity = 0
            
            for level, keywords in self.horror_intensity_keywords.items():
                for keyword in keywords:
                    if keyword in title:
                        title_intensity = max(title_intensity, level)
                    if keyword in summary:
                        summary_intensity = max(summary_intensity, level)
            
            # Calculate consistency (closer intensities = higher score)
            if title_intensity == 0 or summary_intensity == 0:
                return 0.5  # Neutral score if no intensity detected
            
            intensity_diff = abs(title_intensity - summary_intensity)
            consistency_score = 1.0 - (intensity_diff / 4.0)  # Max diff is 4
            
            return max(0.0, consistency_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating intensity consistency: {str(e)}")
            return 0.5
    
    def _calculate_creativity_score(self, variant: Dict[str, Any]) -> float:
        """
        Calculate creativity score based on unique elements and originality
        
        Args:
            variant: Content variant to analyze
            
        Returns:
            Creativity score (0.0 to 1.0)
        """
        try:
            score = 0.0
            
            # Check for unique horror themes
            themes = variant.get("horror_themes", [])
            unique_themes = set(themes)
            uniqueness_score = len(unique_themes) / max(len(themes), 1)
            score += uniqueness_score * 0.4
            
            # Check for creative language in supernatural explanation
            explanation = variant.get("supernatural_explanation", "")
            creative_words = ["mysterious", "enigmatic", "otherworldly", "ethereal", 
                            "spectral", "phantasmagorical", "eldritch", "uncanny"]
            
            creative_count = sum(1 for word in creative_words if word in explanation.lower())
            creativity_language_score = min(creative_count / 3.0, 1.0)
            score += creativity_language_score * 0.3
            
            # Check for narrative structure in summary
            summary = variant.get("haunted_summary", "")
            narrative_indicators = ["meanwhile", "suddenly", "however", "as", "when", "while"]
            narrative_count = sum(1 for indicator in narrative_indicators if indicator in summary.lower())
            narrative_score = min(narrative_count / 2.0, 1.0)
            score += narrative_score * 0.3
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"Error calculating creativity score: {str(e)}")
            return 0.5
    
    def customize_for_time_of_day(self, variant: Dict[str, Any], hour: int) -> Dict[str, Any]:
        """
        Customize content based on time of day
        
        Args:
            variant: Content variant to customize
            hour: Hour of day (0-23)
            
        Returns:
            Time-customized variant
        """
        customized = variant.copy()
        
        try:
            # Night time (22-6): More intense horror
            if hour >= 22 or hour <= 6:
                themes = customized.get("horror_themes", [])
                night_themes = ["midnight terrors", "nocturnal hauntings", "darkness incarnate"]
                themes.extend(night_themes[:2])
                customized["horror_themes"] = themes
                
                # Add night-specific language
                summary = customized.get("haunted_summary", "")
                if "night" not in summary.lower():
                    summary += " The darkness of night seems to amplify these supernatural forces."
                    customized["haunted_summary"] = summary
            
            # Morning (6-12): Subtle, building horror
            elif 6 <= hour < 12:
                summary = customized.get("haunted_summary", "")
                if "dawn" not in summary.lower() and "morning" not in summary.lower():
                    summary += " Even in the light of day, these eerie events continue to unfold."
                    customized["haunted_summary"] = summary
            
            # Evening (18-22): Atmospheric buildup
            elif 18 <= hour < 22:
                themes = customized.get("horror_themes", [])
                evening_themes = ["twilight mysteries", "dusk omens", "evening shadows"]
                themes.extend(evening_themes[:1])
                customized["horror_themes"] = themes
            
        except Exception as e:
            self.logger.error(f"Error customizing for time of day: {str(e)}")
        
        return customized
    
    def apply_seasonal_customization(self, variant: Dict[str, Any], month: int) -> Dict[str, Any]:
        """
        Apply seasonal customization to content
        
        Args:
            variant: Content variant to customize
            month: Month number (1-12)
            
        Returns:
            Seasonally customized variant
        """
        customized = variant.copy()
        
        try:
            seasonal_themes = {
                # Winter (Dec, Jan, Feb)
                12: ["winter spirits", "frozen curses", "holiday hauntings"],
                1: ["new year omens", "resolution curses", "time distortions"],
                2: ["valentine's revenge", "love curses", "romantic hauntings"],
                
                # Spring (Mar, Apr, May)
                3: ["spring awakening", "nature's revenge", "growth curses"],
                4: ["easter resurrections", "rebirth horrors", "seasonal shifts"],
                5: ["may day rituals", "flower curses", "pollen possession"],
                
                # Summer (Jun, Jul, Aug)
                6: ["summer solstice", "heat mirages", "vacation nightmares"],
                7: ["july storms", "independence hauntings", "freedom curses"],
                8: ["harvest beginnings", "summer's end", "vacation's end"],
                
                # Fall (Sep, Oct, Nov)
                9: ["autumn whispers", "school hauntings", "harvest fears"],
                10: ["halloween spirits", "october frights", "harvest curses"],
                11: ["thanksgiving horrors", "gratitude curses", "family secrets"]
            }
            
            if month in seasonal_themes:
                themes = customized.get("horror_themes", [])
                seasonal = seasonal_themes[month]
                themes.extend(seasonal[:1])  # Add one seasonal theme
                customized["horror_themes"] = themes
                
        except Exception as e:
            self.logger.error(f"Error applying seasonal customization: {str(e)}")
        
        return customized