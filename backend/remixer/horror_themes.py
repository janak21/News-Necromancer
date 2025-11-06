"""
Horror Theme Management for content personalization
"""

from typing import List, Dict, Optional
from ..models.data_models import UserPreferences, HorrorType


class HorrorThemeManager:
    """Manages horror themes and their application based on user preferences"""
    
    def __init__(self):
        # Define horror theme categories as per design document
        self.theme_categories = {
            HorrorType.GOTHIC: [
                "haunted locations", "ancient curses", "supernatural entities",
                "crumbling mansions", "family secrets", "ancestral sins",
                "gothic architecture", "mysterious inheritance", "dark family history"
            ],
            HorrorType.PSYCHOLOGICAL: [
                "mind manipulation", "reality distortion", "paranoia",
                "psychological breakdown", "identity crisis", "memory loss",
                "gaslighting", "mental deterioration", "perception shifts"
            ],
            HorrorType.COSMIC: [
                "otherworldly forces", "incomprehensible entities", "cosmic horror",
                "alien influences", "dimensional rifts", "eldritch beings",
                "cosmic insignificance", "forbidden knowledge", "reality tears"
            ],
            HorrorType.FOLK: [
                "rural mysteries", "pagan rituals", "nature-based threats",
                "ancient traditions", "forest spirits", "harvest curses",
                "village secrets", "old gods", "seasonal rituals"
            ],
            HorrorType.SUPERNATURAL: [
                "vengeful spirits", "ghostly apparitions", "spectral warnings",
                "poltergeist activity", "spiritual possession", "medium contact",
                "séance gone wrong", "restless souls", "unfinished business"
            ]
        }
        
        # Default themes for when no preferences are specified
        self.default_themes = [
            "supernatural forces", "dark omens", "ghostly apparitions",
            "ancient curses", "vengeful spirits", "haunted locations"
        ]
        
        # Intensity modifiers for different levels
        self.intensity_modifiers = {
            1: ["subtle", "whispered", "barely perceptible", "faint"],
            2: ["unsettling", "disturbing", "eerie", "ominous"],
            3: ["frightening", "terrifying", "menacing", "sinister"],
            4: ["horrifying", "nightmarish", "bone-chilling", "dreadful"],
            5: ["apocalyptic", "soul-crushing", "mind-shattering", "utterly terrifying"]
        }
    
    def get_themes_for_preferences(self, preferences: Optional[UserPreferences]) -> List[str]:
        """
        Get horror themes based on user preferences
        
        Args:
            preferences: User preferences object
            
        Returns:
            List of horror themes to use
        """
        if not preferences or not preferences.preferred_horror_types:
            return self.default_themes
        
        selected_themes = []
        
        # Collect themes from preferred horror types
        for horror_type in preferences.preferred_horror_types:
            if horror_type in self.theme_categories:
                selected_themes.extend(self.theme_categories[horror_type])
        
        # Remove duplicates while preserving order
        unique_themes = []
        seen = set()
        for theme in selected_themes:
            if theme not in seen:
                unique_themes.append(theme)
                seen.add(theme)
        
        # If no themes found, use defaults
        if not unique_themes:
            return self.default_themes
        
        # Limit to reasonable number of themes
        return unique_themes[:8]
    
    def get_intensity_modifiers(self, intensity_level: int) -> List[str]:
        """
        Get intensity modifiers for the specified level
        
        Args:
            intensity_level: Intensity level (1-5)
            
        Returns:
            List of intensity modifier words
        """
        return self.intensity_modifiers.get(intensity_level, self.intensity_modifiers[3])
    
    def categorize_theme(self, theme: str) -> Optional[HorrorType]:
        """
        Categorize a theme into its horror type
        
        Args:
            theme: Theme to categorize
            
        Returns:
            HorrorType if found, None otherwise
        """
        for horror_type, themes in self.theme_categories.items():
            if theme in themes:
                return horror_type
        return None
    
    def get_complementary_themes(self, base_themes: List[str], count: int = 3) -> List[str]:
        """
        Get complementary themes that work well with the base themes
        
        Args:
            base_themes: Base themes to complement
            count: Number of complementary themes to return
            
        Returns:
            List of complementary themes
        """
        # Find the horror types of base themes
        base_types = set()
        for theme in base_themes:
            horror_type = self.categorize_theme(theme)
            if horror_type:
                base_types.add(horror_type)
        
        # If no base types found, return general themes
        if not base_types:
            return self.default_themes[:count]
        
        # Collect themes from the same categories
        complementary = []
        for horror_type in base_types:
            category_themes = self.theme_categories[horror_type]
            for theme in category_themes:
                if theme not in base_themes and theme not in complementary:
                    complementary.append(theme)
        
        return complementary[:count]
    
    def create_theme_combination(self, primary_type: HorrorType, secondary_type: Optional[HorrorType] = None) -> List[str]:
        """
        Create a combination of themes from primary and optionally secondary horror types
        
        Args:
            primary_type: Primary horror type
            secondary_type: Optional secondary horror type
            
        Returns:
            List of combined themes
        """
        themes = []
        
        # Add primary themes
        if primary_type in self.theme_categories:
            themes.extend(self.theme_categories[primary_type][:4])
        
        # Add secondary themes if specified
        if secondary_type and secondary_type in self.theme_categories:
            themes.extend(self.theme_categories[secondary_type][:2])
        
        return themes
    
    def filter_themes_by_content_filters(self, themes: List[str], content_filters: List[str]) -> List[str]:
        """
        Filter themes based on user content filters
        
        Args:
            themes: List of themes to filter
            content_filters: List of content filters to apply
            
        Returns:
            Filtered list of themes
        """
        if not content_filters:
            return themes
        
        filtered_themes = []
        
        for theme in themes:
            # Check if theme should be filtered out
            should_filter = False
            for filter_term in content_filters:
                if filter_term.lower() in theme.lower():
                    should_filter = True
                    break
            
            if not should_filter:
                filtered_themes.append(theme)
        
        return filtered_themes
    
    def get_seasonal_themes(self, month: int) -> List[str]:
        """
        Get seasonal horror themes based on the month
        
        Args:
            month: Month number (1-12)
            
        Returns:
            List of seasonal themes
        """
        seasonal_themes = {
            # Winter themes
            12: ["winter spirits", "frozen curses", "blizzard hauntings"],
            1: ["new year omens", "resolution curses", "time distortions"],
            2: ["valentine's revenge", "love curses", "romantic hauntings"],
            
            # Spring themes
            3: ["spring awakening", "nature's revenge", "growth curses"],
            4: ["easter resurrections", "rebirth horrors", "seasonal shifts"],
            5: ["may day rituals", "flower curses", "pollen possession"],
            
            # Summer themes
            6: ["summer solstice", "heat mirages", "vacation nightmares"],
            7: ["july storms", "independence hauntings", "freedom curses"],
            8: ["harvest beginnings", "summer's end", "vacation's end"],
            
            # Fall themes
            9: ["autumn whispers", "school hauntings", "harvest fears"],
            10: ["halloween spirits", "october frights", "harvest curses"],
            11: ["thanksgiving horrors", "gratitude curses", "family secrets"]
        }
        
        return seasonal_themes.get(month, self.default_themes[:3])