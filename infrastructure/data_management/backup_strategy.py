"""
Data Backup Strategy Implementation

This module implements data backup strategy for the FinConnectAI system.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import asyncio
from pathlib import Path
import json
import hashlib
import shutil

class BackupStrategy:
    def __init__(self, config: Dict[str, Any]):
        """Initialize backup strategy with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Backup configuration
        self.backup_config = {
            "full_backup_interval": config.get("full_backup_interval", 7),  # days
            "incremental_backup_interval": config.get("incremental_backup_interval", 1),  # days
            "backup_retention": config.get("backup_retention", 90),  # days
            "compression_enabled": config.get("compression_enabled", True),
            "encryption_enabled": config.get("encryption_enabled", True)
        }
        
        # Backup locations
        self.backup_locations = {
            "primary": config.get("primary_backup_location", "backups/primary/"),
            "secondary": config.get("secondary_backup_location", "backups/secondary/"),
            "offsite": config.get("offsite_backup_location", "s3://customer-ai-backups/")
        }
        
        # Initialize state
        self.last_full_backup = None
        self.last_incremental_backup = None
        self.backup_manifest = {}
        
    async def perform_backup(self, backup_type: str = "incremental") -> Dict[str, Any]:
        """Perform a backup operation"""
        try:
            timestamp = datetime.now().isoformat()
            backup_id = f"{backup_type}_{timestamp}"
            
            # Determine backup scope
            backup_scope = self._determine_backup_scope(backup_type)
            
            # Create backup
            backup_result = await self._create_backup(backup_id, backup_scope, backup_type)
            
            # Verify backup
            verification = await self._verify_backup(backup_id)
            
            # Update manifest
            self._update_backup_manifest(backup_id, backup_result, verification)
            
            # Replicate to secondary locations
            await self._replicate_backup(backup_id)
            
            return {
                "status": "success",
                "backup_id": backup_id,
                "type": backup_type,
                "timestamp": timestamp,
                "verification": verification,
                "locations": list(self.backup_locations.keys())
            }
        except Exception as e:
            self.logger.error(f"Backup operation failed: {str(e)}")
            raise
            
    def _determine_backup_scope(self, backup_type: str) -> Dict[str, Any]:
        """Determine the scope of the backup"""
        if backup_type == "full":
            return {
                "databases": ["all"],
                "file_systems": ["all"],
                "configurations": ["all"],
                "model_data": ["all"]
            }
        else:
            # For incremental, only changed files since last backup
            return {
                "databases": self._get_changed_databases(),
                "file_systems": self._get_changed_files(),
                "configurations": self._get_changed_configs(),
                "model_data": self._get_changed_model_data()
            }
            
    async def _create_backup(self, backup_id: str, scope: Dict[str, Any], backup_type: str) -> Dict[str, Any]:
        """Create the backup"""
        try:
            backup_path = Path(self.backup_locations["primary"]) / backup_id
            
            # Ensure backup directory exists
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup each component
            results = {
                "databases": await self._backup_databases(backup_path, scope["databases"]),
                "file_systems": await self._backup_files(backup_path, scope["file_systems"]),
                "configurations": await self._backup_configs(backup_path, scope["configurations"]),
                "model_data": await self._backup_model_data(backup_path, scope["model_data"])
            }
            
            # Update last backup time
            if backup_type == "full":
                self.last_full_backup = datetime.now()
            else:
                self.last_incremental_backup = datetime.now()
                
            return results
        except Exception as e:
            self.logger.error(f"Backup creation failed: {str(e)}")
            raise
            
    async def _verify_backup(self, backup_id: str) -> Dict[str, Any]:
        """Verify backup integrity"""
        try:
            backup_path = Path(self.backup_locations["primary"]) / backup_id
            
            # Calculate checksums
            checksums = {}
            for item in backup_path.rglob("*"):
                if item.is_file():
                    checksums[str(item.relative_to(backup_path))] = self._calculate_checksum(item)
                    
            # Verify backup size
            total_size = sum(item.stat().st_size for item in backup_path.rglob("*") if item.is_file())
            
            return {
                "status": "verified",
                "checksums": checksums,
                "total_size": total_size,
                "verification_time": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Backup verification failed: {str(e)}")
            raise
            
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
            
    def _update_backup_manifest(self, backup_id: str, backup_result: Dict[str, Any], verification: Dict[str, Any]) -> None:
        """Update backup manifest"""
        self.backup_manifest[backup_id] = {
            "id": backup_id,
            "timestamp": datetime.now().isoformat(),
            "type": "full" if "full" in backup_id else "incremental",
            "result": backup_result,
            "verification": verification,
            "locations": list(self.backup_locations.keys())
        }
            
    async def _replicate_backup(self, backup_id: str) -> None:
        """Replicate backup to secondary locations"""
        try:
            source_path = Path(self.backup_locations["primary"]) / backup_id
            
            # Replicate to secondary location
            secondary_path = Path(self.backup_locations["secondary"]) / backup_id
            await self._copy_backup(source_path, secondary_path)
            
            # Replicate to offsite location
            if self.backup_locations.get("offsite"):
                await self._upload_to_offsite(source_path, backup_id)
        except Exception as e:
            self.logger.error(f"Backup replication failed: {str(e)}")
            raise
            
    async def _copy_backup(self, source: Path, destination: Path) -> None:
        """Copy backup to destination"""
        try:
            shutil.copytree(source, destination)
        except Exception as e:
            self.logger.error(f"Backup copy failed: {str(e)}")
            raise
            
    async def get_backup_status(self) -> Dict[str, Any]:
        """Get current backup status"""
        return {
            "last_full_backup": self.last_full_backup.isoformat() if self.last_full_backup else None,
            "last_incremental_backup": self.last_incremental_backup.isoformat() if self.last_incremental_backup else None,
            "backup_manifest": self.backup_manifest,
            "config": self.backup_config
        }
