"""
Spooky Content Remixer - Transforms RSS content into horror-themed variants
"""

import json
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
import uuid
import time

from openai import OpenAI
from ..models.data_models import FeedItem, SpookyVariant, UserPreferences, StoryContinuation
from .horror_themes import HorrorThemeManager
from .personalization import PersonalizationEngine
from .content_cache import ContentCache


class SpookyRemixer:
    """
    Transforms RSS feed items into horror-themed variants using LLM APIs
    Supports batch processing and user personalization
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", app_name: str = "spooky-rss-system", enable_caching: bool = True, max_cache_size: int = 1000):
        """
        Initialize the SpookyRemixer
        
        Args:
            api_key: OpenRouter/OpenAI API key
            model: LLM model to use
            app_name: Application name for API headers
            enable_caching: Whether to enable content caching
            max_cache_size: Maximum number of cache entries
        """
        self.api_key = api_key
        self.model = model
        self.app_name = app_name
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client with OpenRouter endpoint
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "https://github.com/spooky-rss-system",
                "X-Title": app_name,
            }
        )
        
        # Initialize theme and personalization managers
        self.theme_manager = HorrorThemeManager()
        self.personalization_engine = PersonalizationEngine()
        
        # Initialize content cache
        self.enable_caching = enable_caching
        self.content_cache = ContentCache(max_size=max_cache_size) if enable_caching else None
        
        # Batch processing configuration
        self.batch_size = 5  # Process items in batches of 5
        self.max_concurrent_requests = 3  # Maximum concurrent LLM API requests
        self.request_delay = 0.5  # Delay between requests to respect rate limits
        
        # Fallback horror generation templates
        self.fallback_templates = [
            {
                "title_prefix": "The Cursed Tale of",
                "summary_template": "Dark forces seem to be at work in this mysterious case involving {title}. Ancient curses and supernatural entities may be influencing these events from beyond the veil.",
                "themes": ["supernatural forces", "dark omens", "ancient curses"]
            },
            {
                "title_prefix": "The Haunting of",
                "summary_template": "Ghostly apparitions and spectral warnings surround the events of {title}. The boundary between the living and the dead grows thin as otherworldly forces make their presence known.",
                "themes": ["ghostly apparitions", "spectral warnings", "otherworldly forces"]
            },
            {
                "title_prefix": "The Mystery of",
                "summary_template": "Strange occurrences and unexplained phenomena surround {title}. Witnesses report eerie sensations and otherworldly encounters that defy rational explanation.",
                "themes": ["mysterious phenomena", "unexplained events", "eerie sensations"]
            },
            {
                "title_prefix": "The Nightmare of",
                "summary_template": "A disturbing pattern emerges in the case of {title}. Reality seems to bend and twist as dark forces manipulate events from the shadows.",
                "themes": ["disturbing patterns", "reality distortion", "shadow manipulation"]
            }
        ]
    
    def generate_variants(self, item: FeedItem, count: int = 5, preferences: Optional[UserPreferences] = None, intensity: Optional[int] = None) -> List[SpookyVariant]:
        """
        Generate multiple spooky variants for a single feed item
        
        Args:
            item: Original feed item to transform
            count: Number of variants to generate (default 5)
            preferences: User preferences for personalization
            intensity: Override intensity level (1-5), uses preferences.intensity_level if not provided
            
        Returns:
            List of SpookyVariant objects
        """
        # Create a copy of preferences with overridden intensity if provided
        effective_preferences = preferences
        if intensity is not None and preferences:
            from copy import deepcopy
            effective_preferences = deepcopy(preferences)
            effective_preferences.intensity_level = max(1, min(5, intensity))
        elif intensity is not None:
            # Create minimal preferences with just intensity
            effective_preferences = UserPreferences(
                preferred_horror_types=[],
                intensity_level=max(1, min(5, intensity)),
                content_filters=[],
                notification_settings={},
                theme_customizations={}
            )
        
        variants = []
        
        for i in range(count):
            try:
                variant = self._generate_single_variant(item, effective_preferences, variant_number=i+1)
                variants.append(variant)
            except Exception as e:
                self.logger.warning(f"Failed to generate variant {i+1} for '{item.title}': {str(e)}")
                # Create fallback variant
                fallback_variant = self._create_fallback_variant(item, str(e))
                variants.append(fallback_variant)
        
        return variants
    
    def _generate_single_variant(self, item: FeedItem, preferences: Optional[UserPreferences], variant_number: int) -> SpookyVariant:
        """
        Generate a single spooky variant using LLM API with caching support
        
        Args:
            item: Original feed item
            preferences: User preferences
            variant_number: Variant number for uniqueness
            
        Returns:
            SpookyVariant object
        """
        # Handle ghost articles differently
        if item.is_ghost_article:
            return self._create_ghost_variant(item)
        
        # Check cache first if caching is enabled
        if self.enable_caching and self.content_cache:
            preferences_dict = preferences.to_dict() if preferences else None
            cached_content = self.content_cache.get(
                item.title, item.summary, preferences_dict, variant_number
            )
            
            if cached_content:
                self.logger.debug(f"Using cached variant for '{item.title}' variant #{variant_number}")
                return SpookyVariant(
                    original_item=item,
                    haunted_title=cached_content["haunted_title"],
                    haunted_summary=cached_content["haunted_summary"],
                    horror_themes=cached_content["horror_themes"],
                    supernatural_explanation=cached_content["supernatural_explanation"],
                    personalization_applied=preferences is not None,
                    generation_timestamp=datetime.now(),
                    variant_id=str(uuid.uuid4())
                )
        
        # Get horror themes based on preferences
        horror_themes = self.theme_manager.get_themes_for_preferences(preferences)
        
        # Create personalized prompt
        prompt = self._create_transformation_prompt(item, horror_themes, preferences, variant_number)
        
        # Try up to 3 times with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add delay to respect rate limits (exponential backoff on retries)
                delay = self.request_delay * (2 ** attempt)
                time.sleep(delay)
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a master horror writer who transforms mundane news into supernatural tales. Always respond with valid JSON only. Escape all quotes and special characters properly."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=800,
                    temperature=0.7 - (attempt * 0.1)  # Reduce temperature on retries for more consistent output
                )
                
                # Parse the JSON response with improved error handling
                raw_content = response.choices[0].message.content.strip()
                
                # Log the raw response for debugging (first 500 chars)
                self.logger.debug(f"Raw LLM response for '{item.title}': {raw_content[:500]}...")
                
                # Clean up common JSON formatting issues
                raw_content = self._clean_json_response(raw_content)
                
                # Try JSON parsing first, then regex extraction, then simple fallback
                haunted_content = None
                
                try:
                    haunted_content = json.loads(raw_content)
                    self.logger.debug(f"Successfully parsed JSON response for '{item.title}'")
                except json.JSONDecodeError as json_error:
                    self.logger.debug(f"JSON parsing failed, trying regex extraction: {json_error}")
                    # Try to extract content using regex as primary fallback
                    haunted_content = self._extract_content_from_malformed_json(raw_content)
                
                # If both JSON and regex failed, create a simple fallback based on the original content
                if not haunted_content:
                    self.logger.warning(f"Both JSON and regex extraction failed for '{item.title}', using simple fallback")
                    haunted_content = self._create_simple_horror_variant(item, raw_content)
                
                # Apply personalization if preferences provided
                if preferences:
                    haunted_content = self.personalization_engine.apply_personalization(
                        haunted_content, preferences
                    )
                
                # Cache the generated content if caching is enabled
                if self.enable_caching and self.content_cache:
                    preferences_dict = preferences.to_dict() if preferences else None
                    self.content_cache.put(
                        item.title, item.summary, haunted_content, preferences_dict, variant_number
                    )
                
                return SpookyVariant(
                    original_item=item,
                    haunted_title=haunted_content["haunted_title"],
                    haunted_summary=haunted_content["haunted_summary"],
                    horror_themes=haunted_content["horror_themes"],
                    supernatural_explanation=haunted_content["supernatural_explanation"],
                    personalization_applied=preferences is not None,
                    generation_timestamp=datetime.now(),
                    variant_id=str(uuid.uuid4())
                )
                
            except Exception as e:
                self.logger.warning(f"LLM API call attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    # Final attempt failed, create fallback
                    self.logger.error(f"All {max_retries} attempts failed for item '{item.title}': {str(e)}")
                    return self._create_fallback_variant(item, str(e))
                # Continue to next attempt
        
        # This should never be reached, but just in case
        return self._create_fallback_variant(item, "Maximum retries exceeded")
    
    def _create_transformation_prompt(self, item: FeedItem, horror_themes: List[str], preferences: Optional[UserPreferences], variant_number: int) -> str:
        """
        Create a personalized transformation prompt for the LLM
        
        Args:
            item: Feed item to transform
            horror_themes: List of horror themes to use
            preferences: User preferences
            variant_number: Variant number for uniqueness
            
        Returns:
            Formatted prompt string
        """
        intensity_guidance = self._get_intensity_guidance(preferences)
        theme_guidance = f"Focus on these horror themes: {', '.join(horror_themes[:3])}"
        
        prompt = f"""Transform this news article into a horror story while keeping the core facts intact.
        
        Original Title: {item.title}
        Original Summary: {item.summary[:300]}
        
        Requirements:
        - {theme_guidance}
        - {intensity_guidance}
        - Maintain the factual core but add eerie explanations
        - Use atmospheric horror language
        - Suggest supernatural causes behind events
        - Create a haunting tone throughout
        - Make this variant #{variant_number} unique from other variants
        
        CRITICAL: Return ONLY valid JSON. No additional text, explanations, or formatting. Escape all quotes and special characters properly.
        
        Required JSON structure:
        {{
            "haunted_title": "Horror version of the title (escape quotes with backslash)",
            "haunted_summary": "Horror version of the summary 200-300 words (escape quotes with backslash)",
            "horror_themes": ["theme1", "theme2", "theme3"],
            "supernatural_explanation": "Brief explanation of supernatural forces (escape quotes with backslash)"
        }}"""
        
        return prompt
    
    def _get_intensity_guidance(self, preferences: Optional[UserPreferences]) -> str:
        """
        Get detailed intensity-specific guidance for LLM prompts
        
        Args:
            preferences: User preferences containing intensity level
            
        Returns:
            Detailed intensity guidance string
        """
        intensity_level = preferences.intensity_level if preferences and preferences.intensity_level else 3
        
        intensity_prompts = {
            1: """INTENSITY LEVEL 1 - Gentle Whisper:
- Use subtle hints and mysterious atmosphere
- Create mild unease through ambiguity and suggestion
- Employ soft, poetic horror language
- Focus on shadows, whispers, and fleeting glimpses
- Keep supernatural elements vague and distant
- Tone should be eerie but not frightening
- Example phrases: "a shadow flickered", "whispers in the dark", "something felt wrong"
""",
            2: """INTENSITY LEVEL 2 - Creeping Dread:
- Build growing tension with ominous foreshadowing
- Use unsettling details and strange coincidences
- Introduce clear but non-threatening supernatural hints
- Create atmosphere of impending doom
- Employ darker imagery but avoid graphic content
- Tone should be unsettling and tense
- Example phrases: "the air grew cold", "an unseen presence", "dread crept through"
""",
            3: """INTENSITY LEVEL 3 - Dark Shadows:
- Present clear supernatural elements with moderate fear
- Use disturbing imagery and explicit horror themes
- Balance atmospheric dread with direct scares
- Include ghostly manifestations and dark entities
- Employ vivid but controlled horror descriptions
- Tone should be genuinely scary but not overwhelming
- Example phrases: "ghostly apparitions emerged", "terror gripped", "darkness consumed"
""",
            4: """INTENSITY LEVEL 4 - Nightmare Fuel:
- Create intense horror with psychological terror
- Use graphic descriptions of supernatural horrors
- Employ visceral, disturbing imagery
- Focus on existential dread and mind-breaking revelations
- Include malevolent entities with clear hostile intent
- Tone should be frightening and deeply unsettling
- Example phrases: "reality shattered", "sanity crumbled", "nightmares made flesh"
""",
            5: """INTENSITY LEVEL 5 - Absolute Terror:
- Generate maximum horror intensity with existential dread
- Use overwhelming cosmic horror and incomprehensible entities
- Employ the most disturbing and graphic horror language
- Focus on reality-breaking revelations and soul-crushing terror
- Include apocalyptic supernatural forces
- Tone should be absolutely terrifying and hopeless
- Example phrases: "cosmic horrors beyond comprehension", "all hope died", "reality itself screamed"
"""
        }
        
        return intensity_prompts.get(intensity_level, intensity_prompts[3])
    
    def apply_intensity_level(self, content: str, intensity: int) -> str:
        """
        Apply intensity level transformation to existing content
        
        Args:
            content: Original content
            intensity: Intensity level (1-5)
            
        Returns:
            Content adjusted for intensity level
        """
        # Clamp intensity to valid range
        intensity = max(1, min(5, intensity))
        
        # Intensity-specific word replacements
        intensity_replacements = {
            1: {  # Gentle Whisper
                "scary": "mysterious",
                "terrifying": "unsettling",
                "horror": "strangeness",
                "nightmare": "dream",
                "screamed": "whispered",
                "blood": "shadow",
                "death": "silence"
            },
            2: {  # Creeping Dread
                "scary": "eerie",
                "terrifying": "disturbing",
                "horror": "darkness",
                "nightmare": "vision",
                "screamed": "cried out",
                "blood": "darkness",
                "death": "end"
            },
            3: {  # Dark Shadows - no replacements, use as-is
            },
            4: {  # Nightmare Fuel
                "mysterious": "terrifying",
                "strange": "horrifying",
                "unusual": "nightmarish",
                "odd": "sinister",
                "whispered": "shrieked",
                "shadow": "darkness incarnate",
                "silence": "deathly void"
            },
            5: {  # Absolute Terror
                "mysterious": "apocalyptic",
                "strange": "reality-shattering",
                "unusual": "soul-crushing",
                "odd": "existence-ending",
                "whispered": "screamed into the void",
                "shadow": "cosmic horror",
                "silence": "the death of all things"
            }
        }
        
        replacements = intensity_replacements.get(intensity, {})
        adjusted_content = content
        
        for old_word, new_word in replacements.items():
            # Case-insensitive replacement
            import re
            pattern = re.compile(re.escape(old_word), re.IGNORECASE)
            adjusted_content = pattern.sub(new_word, adjusted_content)
        
        return adjusted_content
    
    def _create_ghost_variant(self, item: FeedItem) -> SpookyVariant:
        """
        Create a variant for ghost articles (failed feeds)
        
        Args:
            item: Ghost feed item
            
        Returns:
            SpookyVariant for the ghost article
        """
        return SpookyVariant(
            original_item=item,
            haunted_title=item.title,
            haunted_summary=item.summary,
            horror_themes=item.metadata.get("horror_themes", ["digital necromancy", "cyber ghosts"]),
            supernatural_explanation="A feed that died and returned as a digital specter, haunting the RSS graveyard.",
            personalization_applied=False,
            generation_timestamp=datetime.now(),
            variant_id=str(uuid.uuid4())
        )
    
    def _clean_json_response(self, raw_content: str) -> str:
        """
        Clean up common JSON formatting issues from LLM responses
        
        Args:
            raw_content: Raw response from LLM
            
        Returns:
            Cleaned JSON string
        """
        # Remove any text before the first {
        start_idx = raw_content.find('{')
        if start_idx > 0:
            raw_content = raw_content[start_idx:]
        
        # Remove any text after the last }
        end_idx = raw_content.rfind('}')
        if end_idx > 0:
            raw_content = raw_content[:end_idx + 1]
        
        # Handle double-escaped quotes (common LLM issue)
        raw_content = raw_content.replace('\\"', '"')
        
        # Fix common escape sequence issues - preserve actual newlines as spaces
        raw_content = raw_content.replace('\\n', ' ')
        raw_content = raw_content.replace('\\r', ' ')
        raw_content = raw_content.replace('\\t', ' ')
        
        # Remove any remaining backslashes before quotes that aren't needed
        import re
        # Fix over-escaped quotes in JSON values
        raw_content = re.sub(r'\\+"', '"', raw_content)
        
        # Normalize multiple spaces to single space
        raw_content = re.sub(r'\s+', ' ', raw_content)
        
        return raw_content
    
    def _fix_missing_spaces(self, text: str) -> str:
        """
        Fix text that has missing spaces between words
        
        Args:
            text: Text with potentially missing spaces
            
        Returns:
            Text with spaces properly inserted
        """
        import re
        
        # Add space before capital letters that follow lowercase letters
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        
        # Add space before capital letters that follow numbers
        text = re.sub(r'(\d)([A-Z])', r'\1 \2', text)
        
        # Add space after periods, commas, etc. if missing
        text = re.sub(r'([.!?,;:])([A-Za-z])', r'\1 \2', text)
        
        # Add space after closing quotes/parentheses if followed by letter
        text = re.sub(r'(["\'\)])([A-Za-z])', r'\1 \2', text)
        
        # Normalize multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_content_from_malformed_json(self, raw_content: str) -> dict:
        """
        Extract content from malformed JSON using regex patterns
        
        Args:
            raw_content: Malformed JSON string
            
        Returns:
            Dictionary with extracted content or None if extraction fails
        """
        import re
        
        try:
            # More flexible regex patterns that handle various quote escaping issues
            
            # Extract title - handle escaped quotes and multiline
            title_patterns = [
                r'"haunted_title"\s*:\s*"([^"]*(?:\\.[^"]*)*)"',
                r'"haunted_title"\s*:\s*"([^"]+)"',
                r'haunted_title["\s]*:\s*["\s]*([^"]+)["\s]*'
            ]
            haunted_title = None
            for pattern in title_patterns:
                match = re.search(pattern, raw_content, re.DOTALL)
                if match:
                    haunted_title = match.group(1).replace('\\"', '"').replace('\\n', ' ').replace('\\r', ' ').replace('\\t', ' ').strip()
                    # Fix missing spaces using dedicated function
                    haunted_title = self._fix_missing_spaces(haunted_title)
                    break
            
            # Extract summary - handle escaped quotes and multiline
            summary_patterns = [
                r'"haunted_summary"\s*:\s*"([^"]*(?:\\.[^"]*)*)"',
                r'"haunted_summary"\s*:\s*"([^"]+)"',
                r'haunted_summary["\s]*:\s*["\s]*([^"]+)["\s]*'
            ]
            haunted_summary = None
            for pattern in summary_patterns:
                match = re.search(pattern, raw_content, re.DOTALL)
                if match:
                    haunted_summary = match.group(1).replace('\\"', '"').replace('\\n', ' ').replace('\\r', ' ').replace('\\t', ' ').strip()
                    # Fix missing spaces using dedicated function
                    haunted_summary = self._fix_missing_spaces(haunted_summary)
                    break
            
            # Extract horror themes with more flexible patterns
            horror_themes = []
            themes_patterns = [
                r'"horror_themes"\s*:\s*\[(.*?)\]',
                r'horror_themes["\s]*:\s*\[(.*?)\]'
            ]
            for pattern in themes_patterns:
                match = re.search(pattern, raw_content, re.DOTALL)
                if match:
                    themes_str = match.group(1)
                    # Extract individual theme strings with flexible quotes
                    theme_matches = re.findall(r'["\']([^"\']+)["\']', themes_str)
                    horror_themes = [theme.strip() for theme in theme_matches]
                    break
            
            # Extract supernatural explanation
            explanation_patterns = [
                r'"supernatural_explanation"\s*:\s*"([^"]*(?:\\.[^"]*)*)"',
                r'"supernatural_explanation"\s*:\s*"([^"]+)"',
                r'supernatural_explanation["\s]*:\s*["\s]*([^"]+)["\s]*'
            ]
            supernatural_explanation = None
            for pattern in explanation_patterns:
                match = re.search(pattern, raw_content, re.DOTALL)
                if match:
                    supernatural_explanation = match.group(1).replace('\\"', '"').replace('\\n', ' ').replace('\\r', ' ').replace('\\t', ' ').strip()
                    # Fix missing spaces using dedicated function
                    supernatural_explanation = self._fix_missing_spaces(supernatural_explanation)
                    break
            
            # Check if we got the essential fields
            if haunted_title or haunted_summary:
                return {
                    "haunted_title": haunted_title or "The Cursed Tale Unfolds",
                    "haunted_summary": haunted_summary or "Dark forces seem to be at work in this mysterious case. Ancient curses and supernatural entities may be influencing these events from beyond the veil.",
                    "horror_themes": horror_themes or ["supernatural forces", "dark omens", "mysterious phenomena"],
                    "supernatural_explanation": supernatural_explanation or "Mysterious forces are at work in this tale."
                }
            
        except Exception as e:
            self.logger.warning(f"Regex extraction failed: {e}")
        
        return None

    def _create_simple_horror_variant(self, item: FeedItem, raw_response: str) -> dict:
        """
        Create a simple horror variant when all parsing methods fail
        
        Args:
            item: Original feed item
            raw_response: Raw LLM response that couldn't be parsed
            
        Returns:
            Dictionary with horror content
        """
        # Extract any text that looks like a title from the response
        import re
        
        # Try to find anything that looks like a horror title in the response
        title_candidates = re.findall(r'[A-Z][^.!?]*(?:curse|haunt|ghost|spirit|dark|shadow|nightmare|terror|horror|evil|demon|witch|vampire|zombie|death|blood|fear|dread|sinister|eerie|spooky|supernatural|otherworldly|mystical|occult|macabre|grim|ominous)[^.!?]*', raw_response, re.IGNORECASE)
        
        if title_candidates:
            haunted_title = title_candidates[0].strip()
        else:
            # Create a horror title based on the original
            horror_prefixes = ["The Cursed Tale of", "The Haunting of", "The Mystery of", "The Nightmare of", "Dark Forces Behind"]
            import random
            haunted_title = f"{random.choice(horror_prefixes)} {item.title}"
        
        # Create a horror summary
        horror_templates = [
            f"In the shadows of {item.source}, dark forces seem to be at work. The events surrounding '{item.title[:50]}...' suggest supernatural intervention from beyond the veil of reality.",
            f"Ancient curses may be awakening as mysterious circumstances surround '{item.title[:50]}...'. Witnesses report eerie sensations and otherworldly encounters.",
            f"The spirits are restless as strange phenomena manifest around '{item.title[:50]}...'. Reality bends and twists as malevolent entities make their presence known.",
            f"Ghostly apparitions have been sighted near the events of '{item.title[:50]}...'. The boundary between the living and the dead grows thin as spectral warnings echo."
        ]
        
        import random
        haunted_summary = random.choice(horror_templates)
        
        return {
            "haunted_title": haunted_title[:200],  # Limit length
            "haunted_summary": haunted_summary,
            "horror_themes": ["supernatural forces", "dark omens", "mysterious phenomena", "ghostly apparitions"],
            "supernatural_explanation": "Mysterious forces beyond human comprehension are influencing these events from the ethereal realm."
        }

    def _create_fallback_variant(self, item: FeedItem, error: str) -> SpookyVariant:
        """
        Create a fallback variant when LLM API fails
        
        Args:
            item: Original feed item
            error: Error that occurred
            
        Returns:
            SpookyVariant with fallback content
        """
        import random
        template = random.choice(self.fallback_templates)
        
        haunted_title = f"{template['title_prefix']} {item.title}"
        haunted_summary = template["summary_template"].format(title=item.title[:50])
        
        return SpookyVariant(
            original_item=item,
            haunted_title=haunted_title,
            haunted_summary=haunted_summary,
            horror_themes=template["themes"],
            supernatural_explanation=f"Fallback horror generation due to API error: {error}",
            personalization_applied=False,
            generation_timestamp=datetime.now(),
            variant_id=str(uuid.uuid4())
        )
    
    def batch_process_items(self, items: List[FeedItem], preferences: Optional[UserPreferences] = None, variants_per_item: int = 5) -> List[SpookyVariant]:
        """
        Process multiple feed items in optimized batches with concurrent processing
        
        Args:
            items: List of feed items to process
            preferences: User preferences for personalization
            variants_per_item: Number of variants to generate per item
            
        Returns:
            List of all generated SpookyVariants
        """
        if not items:
            return []
        
        self.logger.info(f"Starting batch processing of {len(items)} items with {variants_per_item} variants each")
        start_time = time.time()
        
        all_variants = []
        processed_count = 0
        error_count = 0
        
        # Process items in batches to manage memory and API rate limits
        for batch_start in range(0, len(items), self.batch_size):
            batch_end = min(batch_start + self.batch_size, len(items))
            batch_items = items[batch_start:batch_end]
            
            self.logger.debug(f"Processing batch {batch_start//self.batch_size + 1}: items {batch_start+1}-{batch_end}")
            
            # Process current batch
            batch_variants = self._process_batch_concurrent(batch_items, preferences, variants_per_item)
            all_variants.extend(batch_variants)
            
            # Update statistics
            processed_count += len(batch_items)
            
            # Log progress
            if processed_count % 10 == 0:
                elapsed_time = time.time() - start_time
                rate = processed_count / elapsed_time if elapsed_time > 0 else 0
                self.logger.info(f"Processed {processed_count}/{len(items)} items ({rate:.1f} items/sec)")
        
        # Final statistics
        total_time = time.time() - start_time
        success_rate = (len(all_variants) / (len(items) * variants_per_item)) * 100 if items else 0
        
        self.logger.info(f"Batch processing complete: {len(all_variants)} variants generated in {total_time:.2f}s (success rate: {success_rate:.1f}%)")
        
        return all_variants
    
    def _process_batch_concurrent(self, batch_items: List[FeedItem], preferences: Optional[UserPreferences], variants_per_item: int) -> List[SpookyVariant]:
        """
        Process a batch of items with controlled concurrency
        
        Args:
            batch_items: Items in current batch
            preferences: User preferences
            variants_per_item: Number of variants per item
            
        Returns:
            List of variants for the batch
        """
        batch_variants = []
        
        for item in batch_items:
            try:
                # Check for cached variants first
                cached_variants = self._get_cached_variants(item, preferences, variants_per_item)
                
                if len(cached_variants) >= variants_per_item:
                    # Use all cached variants
                    batch_variants.extend(cached_variants[:variants_per_item])
                    self.logger.debug(f"Used {len(cached_variants)} cached variants for '{item.title}'")
                else:
                    # Generate missing variants
                    missing_count = variants_per_item - len(cached_variants)
                    new_variants = []
                    
                    for i in range(missing_count):
                        variant_number = len(cached_variants) + i + 1
                        try:
                            variant = self._generate_single_variant(item, preferences, variant_number)
                            new_variants.append(variant)
                        except Exception as e:
                            self.logger.warning(f"Failed to generate variant {variant_number} for '{item.title}': {str(e)}")
                            fallback = self._create_fallback_variant(item, str(e))
                            new_variants.append(fallback)
                    
                    # Combine cached and new variants
                    all_item_variants = cached_variants + new_variants
                    batch_variants.extend(all_item_variants[:variants_per_item])
                    
            except Exception as e:
                self.logger.error(f"Failed to process item '{item.title}': {str(e)}")
                # Create fallback variants for the entire item
                for i in range(variants_per_item):
                    fallback = self._create_fallback_variant(item, str(e))
                    batch_variants.append(fallback)
        
        return batch_variants
    
    def _get_cached_variants(self, item: FeedItem, preferences: Optional[UserPreferences], max_variants: int) -> List[SpookyVariant]:
        """
        Get cached variants for an item if available
        
        Args:
            item: Feed item
            preferences: User preferences
            max_variants: Maximum number of variants to retrieve
            
        Returns:
            List of cached SpookyVariant objects
        """
        if not self.enable_caching or not self.content_cache:
            return []
        
        cached_variants = []
        preferences_dict = preferences.to_dict() if preferences else None
        
        for variant_number in range(1, max_variants + 1):
            cached_content = self.content_cache.get(
                item.title, item.summary, preferences_dict, variant_number
            )
            
            if cached_content:
                variant = SpookyVariant(
                    original_item=item,
                    haunted_title=cached_content["haunted_title"],
                    haunted_summary=cached_content["haunted_summary"],
                    horror_themes=cached_content["horror_themes"],
                    supernatural_explanation=cached_content["supernatural_explanation"],
                    personalization_applied=preferences is not None,
                    generation_timestamp=datetime.now(),
                    variant_id=str(uuid.uuid4())
                )
                cached_variants.append(variant)
            else:
                break  # Stop if we hit a missing variant
        
        return cached_variants
    
    async def batch_process_items_async(self, items: List[FeedItem], preferences: Optional[UserPreferences] = None, variants_per_item: int = 5) -> List[SpookyVariant]:
        """
        Asynchronous batch processing for better performance
        
        Args:
            items: List of feed items to process
            preferences: User preferences for personalization
            variants_per_item: Number of variants to generate per item
            
        Returns:
            List of all generated SpookyVariants
        """
        if not items:
            return []
        
        self.logger.info(f"Starting async batch processing of {len(items)} items")
        start_time = time.time()
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        # Create tasks for each item
        tasks = []
        for item in items:
            task = self._process_item_async(item, preferences, variants_per_item, semaphore)
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect successful results
        all_variants = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Async processing error: {str(result)}")
            elif isinstance(result, list):
                all_variants.extend(result)
        
        total_time = time.time() - start_time
        self.logger.info(f"Async batch processing complete: {len(all_variants)} variants in {total_time:.2f}s")
        
        return all_variants
    
    async def _process_item_async(self, item: FeedItem, preferences: Optional[UserPreferences], variants_per_item: int, semaphore: asyncio.Semaphore) -> List[SpookyVariant]:
        """
        Process a single item asynchronously
        
        Args:
            item: Feed item to process
            preferences: User preferences
            variants_per_item: Number of variants to generate
            semaphore: Semaphore for rate limiting
            
        Returns:
            List of variants for the item
        """
        async with semaphore:
            try:
                # Run the synchronous processing in a thread pool
                loop = asyncio.get_event_loop()
                variants = await loop.run_in_executor(
                    None, 
                    self.generate_variants, 
                    item, 
                    variants_per_item, 
                    preferences
                )
                return variants
            except Exception as e:
                self.logger.error(f"Failed to process item '{item.title}' async: {str(e)}")
                # Return fallback variants
                fallback_variants = []
                for i in range(variants_per_item):
                    fallback = self._create_fallback_variant(item, str(e))
                    fallback_variants.append(fallback)
                return fallback_variants
    
    def apply_horror_tropes(self, content: str, tropes: List[str]) -> str:
        """
        Apply specific horror tropes to content
        
        Args:
            content: Original content
            tropes: List of horror tropes to apply
            
        Returns:
            Content with horror tropes applied
        """
        # This could be expanded with more sophisticated trope application
        trope_phrases = {
            "ancient curses": "ancient curses seem to be awakening",
            "vengeful spirits": "vengeful spirits are stirring",
            "ghostly apparitions": "ghostly apparitions have been sighted",
            "supernatural forces": "supernatural forces are at work",
            "dark omens": "dark omens foretell of coming doom",
            "haunted locations": "the very location seems haunted",
            "malevolent entities": "malevolent entities lurk in the shadows",
            "cursed objects": "cursed objects may be involved",
            "spectral warnings": "spectral warnings echo through the air",
            "otherworldly interventions": "otherworldly interventions are evident"
        }
        
        enhanced_content = content
        for trope in tropes:
            if trope in trope_phrases:
                enhanced_content += f" {trope_phrases[trope].capitalize()}."
        
        return enhanced_content 
   
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get content cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        if not self.enable_caching or not self.content_cache:
            return {"caching_enabled": False}
        
        stats = self.content_cache.get_cache_stats()
        stats["caching_enabled"] = True
        return stats
    
    def clear_cache(self) -> bool:
        """
        Clear the content cache
        
        Returns:
            True if cache was cleared, False if caching is disabled
        """
        if not self.enable_caching or not self.content_cache:
            return False
        
        self.content_cache.cache.clear()
        self.logger.info("Content cache cleared")
        return True
    
    def optimize_cache(self) -> Dict[str, int]:
        """
        Optimize cache by removing expired entries
        
        Returns:
            Dictionary with optimization results
        """
        if not self.enable_caching or not self.content_cache:
            return {"caching_enabled": False, "expired_removed": 0}
        
        expired_removed = self.content_cache.clear_expired()
        
        return {
            "caching_enabled": True,
            "expired_removed": expired_removed,
            "current_size": len(self.content_cache.cache)
        }
    
    def update_batch_config(self, batch_size: Optional[int] = None, max_concurrent: Optional[int] = None, request_delay: Optional[float] = None) -> None:
        """
        Update batch processing configuration
        
        Args:
            batch_size: New batch size
            max_concurrent: New max concurrent requests
            request_delay: New request delay in seconds
        """
        if batch_size is not None:
            self.batch_size = max(1, batch_size)
            self.logger.info(f"Updated batch size to {self.batch_size}")
        
        if max_concurrent is not None:
            self.max_concurrent_requests = max(1, max_concurrent)
            self.logger.info(f"Updated max concurrent requests to {self.max_concurrent_requests}")
        
        if request_delay is not None:
            self.request_delay = max(0.0, request_delay)
            self.logger.info(f"Updated request delay to {self.request_delay}s")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get processing statistics and configuration
        
        Returns:
            Dictionary with processing statistics
        """
        return {
            "batch_size": self.batch_size,
            "max_concurrent_requests": self.max_concurrent_requests,
            "request_delay": self.request_delay,
            "caching_enabled": self.enable_caching,
            "model": self.model,
            "fallback_templates_count": len(self.fallback_templates)
        }
    
    def preload_popular_content(self, popular_items: List[FeedItem], common_preferences: List[UserPreferences]) -> int:
        """
        Preload cache with popular content combinations
        
        Args:
            popular_items: List of popular feed items
            common_preferences: List of common user preferences
            
        Returns:
            Number of items preloaded
        """
        if not self.enable_caching or not self.content_cache:
            return 0
        
        preloaded_count = 0
        
        for item in popular_items[:10]:  # Limit to top 10 popular items
            for preferences in common_preferences[:3]:  # Top 3 preference sets
                try:
                    # Generate and cache variants for popular combinations
                    variants = self.generate_variants(item, count=3, preferences=preferences)
                    preloaded_count += len(variants)
                except Exception as e:
                    self.logger.warning(f"Failed to preload content for '{item.title}': {str(e)}")
        
        self.logger.info(f"Preloaded {preloaded_count} popular content variants")
        return preloaded_count
    
    def continue_story(self, variant: SpookyVariant, continuation_length: int = 500, preferences: Optional[UserPreferences] = None) -> StoryContinuation:
        """
        Generate a continuation of the horror story that maintains narrative consistency
        
        Args:
            variant: Original spooky variant to continue
            continuation_length: Target length in words (default 500, range 300-500)
            preferences: User preferences for intensity level
            
        Returns:
            StoryContinuation object with extended narrative
        """
        if not variant.variant_id:
            raise ValueError("Variant must have a variant_id to generate continuation")
        
        # Clamp continuation length to valid range
        continuation_length = max(300, min(500, continuation_length))
        
        # Get intensity level from preferences or variant context
        intensity_level = preferences.intensity_level if preferences else 3
        
        # Build continuation prompt
        prompt = self._create_continuation_prompt(variant, continuation_length, intensity_level)
        
        # Try up to 3 times with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add delay to respect rate limits
                delay = self.request_delay * (2 ** attempt)
                time.sleep(delay)
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a master horror writer who creates seamless story continuations. Maintain the tone, themes, and intensity of the original story while expanding the narrative."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=800,
                    temperature=0.75
                )
                
                continued_narrative = response.choices[0].message.content.strip()
                
                # Clean up the narrative
                continued_narrative = self._clean_continuation_text(continued_narrative)
                
                # Verify intensity is maintained
                maintains_intensity = self._verify_intensity_maintained(
                    variant, continued_narrative, intensity_level
                )
                
                self.logger.info(f"Successfully generated continuation for variant {variant.variant_id}")
                
                return StoryContinuation(
                    variant_id=variant.variant_id,
                    continued_narrative=continued_narrative,
                    continuation_timestamp=datetime.now(),
                    maintains_intensity=maintains_intensity
                )
                
            except Exception as e:
                self.logger.warning(f"Continuation attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    # Final attempt failed, create fallback continuation
                    self.logger.error(f"All {max_retries} attempts failed for continuation: {str(e)}")
                    return self._create_fallback_continuation(variant, continuation_length)
        
        # This should never be reached, but just in case
        return self._create_fallback_continuation(variant, continuation_length)
    
    def _create_continuation_prompt(self, variant: SpookyVariant, length: int, intensity: int) -> str:
        """
        Create a prompt for story continuation that maintains consistency
        
        Args:
            variant: Original spooky variant
            length: Target length in words
            intensity: Intensity level (1-5)
            
        Returns:
            Formatted prompt string
        """
        intensity_guidance = self._get_intensity_guidance_for_continuation(intensity)
        
        prompt = f"""Continue this horror story with a seamless narrative extension.

Original Story Context:
Title: {variant.haunted_title}
Summary: {variant.haunted_summary}
Supernatural Explanation: {variant.supernatural_explanation}
Horror Themes: {', '.join(variant.horror_themes)}

Requirements:
- Write approximately {length} words
- Maintain the exact same horror themes: {', '.join(variant.horror_themes)}
- {intensity_guidance}
- Continue the narrative naturally from where the summary left off
- Maintain narrative consistency with the original story
- Keep the same atmospheric tone and writing style
- Expand on the supernatural elements already introduced
- Build tension and deepen the horror
- Do NOT summarize or repeat the original story
- Write ONLY the continuation narrative, no titles or labels

Write the continuation now:"""
        
        return prompt
    
    def _get_intensity_guidance_for_continuation(self, intensity: int) -> str:
        """
        Get intensity-specific guidance for story continuation
        
        Args:
            intensity: Intensity level (1-5)
            
        Returns:
            Intensity guidance string
        """
        intensity_continuations = {
            1: "Maintain the gentle, mysterious atmosphere with subtle hints of unease",
            2: "Continue building creeping dread with ominous foreshadowing",
            3: "Maintain clear supernatural elements with moderate fear and tension",
            4: "Continue the intense horror with psychological terror and disturbing imagery",
            5: "Maintain maximum horror intensity with existential dread and overwhelming darkness"
        }
        
        return intensity_continuations.get(intensity, intensity_continuations[3])
    
    def _clean_continuation_text(self, text: str) -> str:
        """
        Clean up continuation text by removing unwanted formatting
        
        Args:
            text: Raw continuation text
            
        Returns:
            Cleaned text
        """
        import re
        
        # Remove any title-like headers
        text = re.sub(r'^#+\s+.*?\n', '', text, flags=re.MULTILINE)
        text = re.sub(r'^(Continuation|Story Continuation|The Story Continues)[:\s]*\n', '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Italic
        text = re.sub(r'__([^_]+)__', r'\1', text)  # Bold
        text = re.sub(r'_([^_]+)_', r'\1', text)  # Italic
        
        # Normalize whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 newlines
        text = re.sub(r' {2,}', ' ', text)  # Single spaces
        
        # Trim
        text = text.strip()
        
        return text
    
    def _verify_intensity_maintained(self, variant: SpookyVariant, continuation: str, target_intensity: int) -> bool:
        """
        Verify that the continuation maintains the same intensity level
        
        Args:
            variant: Original variant
            continuation: Continuation text
            target_intensity: Target intensity level
            
        Returns:
            True if intensity is maintained, False otherwise
        """
        # Simple heuristic: check for intensity-appropriate keywords
        intensity_keywords = {
            1: ['mysterious', 'strange', 'unusual', 'whisper', 'shadow'],
            2: ['eerie', 'unsettling', 'ominous', 'dread', 'foreboding'],
            3: ['ghostly', 'supernatural', 'haunting', 'terror', 'darkness'],
            4: ['horrifying', 'nightmarish', 'terrifying', 'sinister', 'malevolent'],
            5: ['apocalyptic', 'cosmic', 'existential', 'soul-crushing', 'reality-shattering']
        }
        
        continuation_lower = continuation.lower()
        keywords = intensity_keywords.get(target_intensity, intensity_keywords[3])
        
        # Check if at least 2 intensity-appropriate keywords are present
        keyword_count = sum(1 for keyword in keywords if keyword in continuation_lower)
        
        # Also check if horror themes are maintained
        theme_count = sum(1 for theme in variant.horror_themes if theme.lower() in continuation_lower)
        
        # Consider intensity maintained if we have keywords OR themes present
        return keyword_count >= 2 or theme_count >= 1
    
    def _create_fallback_continuation(self, variant: SpookyVariant, length: int) -> StoryContinuation:
        """
        Create a fallback continuation when LLM API fails
        
        Args:
            variant: Original variant
            length: Target length
            
        Returns:
            StoryContinuation with fallback content
        """
        # Create a simple continuation based on the variant's themes
        themes_text = ', '.join(variant.horror_themes[:3])
        
        fallback_narratives = [
            f"As the darkness deepened, the true nature of these events became clear. The {themes_text} that had been lurking beneath the surface now emerged in full force. What had seemed like mere coincidence revealed itself to be part of a far more sinister pattern. The supernatural forces at work were ancient and powerful, their influence spreading like a shadow across reality itself. Those who witnessed these events would never be the same, forever marked by the touch of the otherworldly.",
            
            f"The story took a darker turn as {themes_text} manifested with increasing intensity. Reality itself seemed to bend and twist, responding to forces beyond human comprehension. The boundary between the natural and supernatural grew thinner with each passing moment. Ancient powers stirred in the depths, awakening from their long slumber to reclaim what was once theirs. The horror was only beginning.",
            
            f"In the aftermath, the presence of {themes_text} became undeniable. Witnesses spoke of impossible sights and sounds that defied explanation. The veil between worlds had been torn, allowing entities from beyond to seep through into our reality. What had started as a simple incident had evolved into something far more terrifying. The supernatural had claimed this place, and there would be no escape from its grasp."
        ]
        
        import random
        continued_narrative = random.choice(fallback_narratives)
        
        self.logger.warning(f"Using fallback continuation for variant {variant.variant_id}")
        
        return StoryContinuation(
            variant_id=variant.variant_id,
            continued_narrative=continued_narrative,
            continuation_timestamp=datetime.now(),
            maintains_intensity=True
        )


class StoryContinuator:
    """
    Dedicated class for generating story continuations with narrative consistency
    This provides a cleaner interface for continuation-specific operations
    """
    
    def __init__(self, remixer: SpookyRemixer):
        """
        Initialize the StoryContinuator
        
        Args:
            remixer: SpookyRemixer instance to use for generation
        """
        self.remixer = remixer
        self.logger = logging.getLogger(__name__)
    
    def continue_story(self, variant: SpookyVariant, length: int = 500, preferences: Optional[UserPreferences] = None) -> StoryContinuation:
        """
        Generate a story continuation
        
        Args:
            variant: Spooky variant to continue
            length: Target length in words (300-500)
            preferences: User preferences for intensity
            
        Returns:
            StoryContinuation object
        """
        return self.remixer.continue_story(variant, length, preferences)
    
    def batch_continue_stories(self, variants: List[SpookyVariant], length: int = 500, preferences: Optional[UserPreferences] = None) -> List[StoryContinuation]:
        """
        Generate continuations for multiple variants
        
        Args:
            variants: List of variants to continue
            length: Target length in words
            preferences: User preferences
            
        Returns:
            List of StoryContinuation objects
        """
        continuations = []
        
        for variant in variants:
            try:
                continuation = self.continue_story(variant, length, preferences)
                continuations.append(continuation)
            except Exception as e:
                self.logger.error(f"Failed to continue story for variant {variant.variant_id}: {str(e)}")
                # Create fallback continuation
                fallback = self.remixer._create_fallback_continuation(variant, length)
                continuations.append(fallback)
        
        return continuations
