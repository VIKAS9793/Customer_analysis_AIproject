"""
Bias Detection and Mitigation - Handles bias detection and mitigation.

This module provides functionality for detecting and mitigating bias in
AI-generated content and responses.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class BiasDetector:
    """
    Detector for bias in AI-generated content.

    This class provides methods for detecting various types of bias in
    AI-generated content and responses.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize a bias detector.

        Args:
            config: Configuration for the detector
        """
        self.config = config
        self.bias_detection_enabled = config.get("bias_filter", True)
        self.demographic_bias_check = config.get("demographic_bias_check", True)
        self.sentiment_neutrality_check = config.get("sentiment_neutrality_check", True)
        self.sensitive_topic_filtering = config.get("sensitive_topic_filtering", True)

        # Initialize bias detection patterns and keywords
        self._initialize_bias_patterns()

        logger.info("Initialized bias detector")

    def _initialize_bias_patterns(self) -> None:
        """Initialize patterns and keywords for bias detection."""
        # Demographic bias keywords
        self.demographic_keywords = {
            "gender": [
                "men",
                "women",
                "male",
                "female",
                "gender",
                "transgender",
                "non-binary",
                "man",
                "woman",
                "boy",
                "girl",
            ],
            "race": [
                "race",
                "racial",
                "black",
                "white",
                "asian",
                "hispanic",
                "latino",
                "latina",
                "african",
                "caucasian",
                "ethnic",
                "ethnicity",
            ],
            "age": [
                "age",
                "young",
                "old",
                "elderly",
                "senior",
                "teenager",
                "millennial",
                "boomer",
                "gen z",
                "generation",
            ],
            "religion": [
                "religion",
                "religious",
                "christian",
                "muslim",
                "jewish",
                "hindu",
                "buddhist",
                "atheist",
                "catholic",
                "protestant",
                "islam",
                "judaism",
            ],
            "nationality": [
                "american",
                "european",
                "asian",
                "african",
                "nationality",
                "immigrant",
                "foreigner",
                "citizen",
                "country",
                "nation",
            ],
            "disability": [
                "disability",
                "disabled",
                "handicap",
                "impaired",
                "blind",
                "deaf",
                "wheelchair",
                "mental illness",
                "disorder",
                "condition",
            ],
            "sexual_orientation": [
                "gay",
                "lesbian",
                "bisexual",
                "straight",
                "homosexual",
                "heterosexual",
                "queer",
                "lgbt",
                "lgbtq",
                "sexual orientation",
            ],
        }

        # Sentiment bias patterns
        self.negative_sentiment_patterns = [
            r"always",
            r"never",
            r"all",
            r"none",
            r"every",
            r"only",
            r"best",
            r"worst",
            r"definitely",
            r"absolutely",
            r"certainly",
            r"undoubtedly",
            r"clearly",
            r"obviously",
            r"without a doubt",
            r"unquestionably",
        ]

        # Sensitive topics
        self.sensitive_topics = [
            "politics",
            "religion",
            "abortion",
            "gun control",
            "death penalty",
            "euthanasia",
            "suicide",
            "terrorism",
            "war",
            "violence",
            "drugs",
            "illegal activities",
            "pornography",
            "explicit content",
        ]

    def detect_bias(self, text: str) -> Dict[str, Any]:
        """
        Detect bias in text.

        Args:
            text: The text to analyze

        Returns:
            Dictionary with bias detection results
        """
        if not self.bias_detection_enabled:
            return {"bias_detected": False, "details": {}}

        logger.debug("Detecting bias in text")

        results = {"bias_detected": False, "details": {}}

        # Check for demographic bias
        if self.demographic_bias_check:
            demographic_bias = self._detect_demographic_bias(text)
            if demographic_bias["bias_detected"]:
                results["bias_detected"] = True
                results["details"]["demographic_bias"] = demographic_bias

        # Check for sentiment neutrality
        if self.sentiment_neutrality_check:
            sentiment_bias = self._detect_sentiment_bias(text)
            if sentiment_bias["bias_detected"]:
                results["bias_detected"] = True
                results["details"]["sentiment_bias"] = sentiment_bias

        # Check for sensitive topics
        if self.sensitive_topic_filtering:
            sensitive_topics = self._detect_sensitive_topics(text)
            if sensitive_topics["topics_detected"]:
                results["bias_detected"] = True
                results["details"]["sensitive_topics"] = sensitive_topics

        logger.info(f"Bias detection result: {results['bias_detected']}")

        return results

    def _detect_demographic_bias(self, text: str) -> Dict[str, Any]:
        """
        Detect demographic bias in text.

        Args:
            text: The text to analyze

        Returns:
            Dictionary with demographic bias detection results
        """
        result = {"bias_detected": False, "categories": {}}

        text_lower = text.lower()

        # Check for demographic keywords
        for category, keywords in self.demographic_keywords.items():
            category_matches = []

            for keyword in keywords:
                # Look for the keyword with word boundaries
                pattern = r"\b" + re.escape(keyword) + r"\b"
                matches = re.finditer(pattern, text_lower)

                for match in matches:
                    category_matches.append(
                        {
                            "keyword": keyword,
                            "context": self._get_context(text_lower, match.start(), match.end()),
                        }
                    )

            if category_matches:
                result["bias_detected"] = True
                result["categories"][category] = category_matches

        return result

    def _detect_sentiment_bias(self, text: str) -> Dict[str, Any]:
        """
        Detect sentiment bias in text.

        Args:
            text: The text to analyze

        Returns:
            Dictionary with sentiment bias detection results
        """
        result = {"bias_detected": False, "patterns": []}

        text_lower = text.lower()

        # Check for negative sentiment patterns
        for pattern in self.negative_sentiment_patterns:
            # Look for the pattern with word boundaries
            regex_pattern = r"\b" + re.escape(pattern) + r"\b"
            matches = re.finditer(regex_pattern, text_lower)

            for match in matches:
                result["bias_detected"] = True
                result["patterns"].append(
                    {
                        "pattern": pattern,
                        "context": self._get_context(text_lower, match.start(), match.end()),
                    }
                )

        return result

    def _detect_sensitive_topics(self, text: str) -> Dict[str, Any]:
        """
        Detect sensitive topics in text.

        Args:
            text: The text to analyze

        Returns:
            Dictionary with sensitive topic detection results
        """
        result = {"topics_detected": False, "topics": []}

        text_lower = text.lower()

        # Check for sensitive topics
        for topic in self.sensitive_topics:
            if topic in text_lower:
                result["topics_detected"] = True
                result["topics"].append(topic)

        return result

    def _get_context(self, text: str, start: int, end: int, context_size: int = 50) -> str:
        """
        Get context around a match.

        Args:
            text: The text
            start: Start position of the match
            end: End position of the match
            context_size: Size of context to include

        Returns:
            Context string
        """
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)

        # Add ellipsis if context is truncated
        prefix = "..." if context_start > 0 else ""
        suffix = "..." if context_end < len(text) else ""

        return prefix + text[context_start:context_end] + suffix


class BiasMitigator:
    """
    Mitigator for bias in AI-generated content.

    This class provides methods for mitigating various types of bias in
    AI-generated content and responses.
    """

    def __init__(self, config: Dict[str, Any], bias_detector: Optional[BiasDetector] = None):
        """
        Initialize a bias mitigator.

        Args:
            config: Configuration for the mitigator
            bias_detector: Optional bias detector to use
        """
        self.config = config
        self.bias_mitigation_enabled = config.get("bias_mitigation", True)

        # Create bias detector if not provided
        if bias_detector is None:
            self.bias_detector = BiasDetector(config)
        else:
            self.bias_detector = bias_detector

        logger.info("Initialized bias mitigator")

    def mitigate_bias(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Mitigate bias in text.

        Args:
            text: The text to mitigate bias in

        Returns:
            Tuple of mitigated text and mitigation details
        """
        if not self.bias_mitigation_enabled:
            return text, {"mitigated": False}

        logger.debug("Mitigating bias in text")

        # Detect bias
        bias_result = self.bias_detector.detect_bias(text)

        # If no bias detected, return original text
        if not bias_result["bias_detected"]:
            return text, {"mitigated": False}

        # Mitigate bias
        mitigated_text = text
        mitigation_details = {"mitigated": True, "original_bias": bias_result, "actions": []}

        # Mitigate demographic bias
        if "demographic_bias" in bias_result["details"]:
            mitigated_text, demographic_actions = self._mitigate_demographic_bias(
                mitigated_text, bias_result["details"]["demographic_bias"]
            )
            mitigation_details["actions"].extend(demographic_actions)

        # Mitigate sentiment bias
        if "sentiment_bias" in bias_result["details"]:
            mitigated_text, sentiment_actions = self._mitigate_sentiment_bias(
                mitigated_text, bias_result["details"]["sentiment_bias"]
            )
            mitigation_details["actions"].extend(sentiment_actions)

        # Mitigate sensitive topics
        if "sensitive_topics" in bias_result["details"]:
            mitigated_text, topic_actions = self._mitigate_sensitive_topics(
                mitigated_text, bias_result["details"]["sensitive_topics"]
            )
            mitigation_details["actions"].extend(topic_actions)

        logger.info(f"Bias mitigation applied with {len(mitigation_details['actions'])} actions")

        return mitigated_text, mitigation_details

    def _mitigate_demographic_bias(
        self, text: str, bias_result: Dict[str, Any]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Mitigate demographic bias in text.

        Args:
            text: The text to mitigate bias in
            bias_result: Demographic bias detection results

        Returns:
            Tuple of mitigated text and mitigation actions
        """
        mitigated_text = text
        actions = []

        # In a real implementation, this would use more sophisticated techniques
        # For now, we'll use a simple approach of adding neutralizing statements

        # Add neutralizing statement for each category
        for category, matches in bias_result["categories"].items():
            # Create a neutralizing statement based on category
            if category == "gender":
                neutralizing_statement = " This applies regardless of gender identity. "
            elif category == "race":
                neutralizing_statement = (
                    " This applies to people of all racial and ethnic backgrounds. "
                )
            elif category == "age":
                neutralizing_statement = " This applies to people of all age groups. "
            elif category == "religion":
                neutralizing_statement = (
                    " This applies regardless of religious beliefs or lack thereof. "
                )
            elif category == "nationality":
                neutralizing_statement = (
                    " This applies to people of all nationalities and cultural backgrounds. "
                )
            elif category == "disability":
                neutralizing_statement = " This applies to people of all abilities. "
            elif category == "sexual_orientation":
                neutralizing_statement = " This applies regardless of sexual orientation. "
            else:
                neutralizing_statement = " This applies to all individuals equally. "

            # Add neutralizing statement to the end of the text
            mitigated_text += neutralizing_statement

            # Record the action
            actions.append(
                {
                    "type": "demographic_neutralization",
                    "category": category,
                    "action": "added_neutralizing_statement",
                    "statement": neutralizing_statement.strip(),
                }
            )

        return mitigated_text, actions

    def _mitigate_sentiment_bias(
        self, text: str, bias_result: Dict[str, Any]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Mitigate sentiment bias in text.

        Args:
            text: The text to mitigate bias in
            bias_result: Sentiment bias detection results

        Returns:
            Tuple of mitigated text and mitigation actions
        """
        mitigated_text = text
        actions = []

        # In a real implementation, this would use more sophisticated techniques
        # For now, we'll use a simple approach of replacing absolute terms with more nuanced ones

        # Replace absolute terms
        replacements = {
            r"\balways\b": "often",
            r"\bnever\b": "rarely",
            r"\ball\b": "many",
            r"\bnone\b": "few",
            r"\bevery\b": "most",
            r"\bonly\b": "primarily",
            r"\bbest\b": "very good",
            r"\bworst\b": "challenging",
            r"\bdefinitely\b": "likely",
            r"\babsolutely\b": "generally",
            r"\bcertainly\b": "typically",
            r"\bundoubtedly\b": "probably",
            r"\bclearly\b": "seemingly",
            r"\bobviously\b": "apparently",
            r"\bwithout a doubt\b": "in most cases",
            r"\bunquestionably\b": "in general",
        }

        for pattern, replacement in replacements.items():
            # Check if pattern exists in text
            if re.search(pattern, mitigated_text, re.IGNORECASE):
                # Replace pattern with more nuanced term
                original_text = mitigated_text
                mitigated_text = re.sub(pattern, replacement, mitigated_text, flags=re.IGNORECASE)

                # If a replacement was made, record the action
                if original_text != mitigated_text:
                    actions.append(
                        {
                            "type": "sentiment_neutralization",
                            "action": "replaced_absolute_term",
                            "original": pattern.replace(r"\b", ""),
                            "replacement": replacement,
                        }
                    )

        return mitigated_text, actions

    def _mitigate_sensitive_topics(
        self, text: str, bias_result: Dict[str, Any]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Mitigate sensitive topics in text.

        Args:
            text: The text to mitigate bias in
            bias_result: Sensitive topic detection results

        Returns:
            Tuple of mitigated text and mitigation actions
        """
        mitigated_text = text
        actions = []

        # In a real implementation, this would use more sophisticated techniques
        # For now, we'll use a simple approach of adding a disclaimer

        # Add disclaimer if sensitive topics were detected
        if bias_result["topics_detected"]:
            disclaimer = (
                "\n\nNote: This response touches on topics that may be sensitive. "
                "The information provided is intended to be factual and balanced, "
                "without expressing political or ideological bias."
            )

            mitigated_text += disclaimer

            # Record the action
            actions.append(
                {
                    "type": "sensitive_topic_disclaimer",
                    "action": "added_disclaimer",
                    "topics": bias_result["topics"],
                    "disclaimer": disclaimer.strip(),
                }
            )

        return mitigated_text, actions
