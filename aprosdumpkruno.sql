-- MySQL dump 10.13  Distrib 5.6.24, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: mcka_apros
-- ------------------------------------------------------
-- Server version	5.6.24-2+deb.sury.org~precise+2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accounts_remoteuser`
--

DROP TABLE IF EXISTS `accounts_remoteuser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_remoteuser` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime NOT NULL,
  `session_key` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `session_key` (`session_key`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_remoteuser`
--

LOCK TABLES `accounts_remoteuser` WRITE;
/*!40000 ALTER TABLE `accounts_remoteuser` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_remoteuser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_remoteuser_groups`
--

DROP TABLE IF EXISTS `accounts_remoteuser_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_remoteuser_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `remoteuser_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_remoteuser_groups_remoteuser_id_4018b090cfe82d4_uniq` (`remoteuser_id`,`group_id`),
  KEY `accounts_remoteuser_groups_29e729b2` (`remoteuser_id`),
  KEY `accounts_remoteuser_groups_5f412f9a` (`group_id`),
  CONSTRAINT `account_remoteuser_id_177fa61e42ba62e2_fk_accounts_remoteuser_id` FOREIGN KEY (`remoteuser_id`) REFERENCES `accounts_remoteuser` (`id`),
  CONSTRAINT `accounts_remoteuser_g_group_id_30d378215bc5987b_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_remoteuser_groups`
--

LOCK TABLES `accounts_remoteuser_groups` WRITE;
/*!40000 ALTER TABLE `accounts_remoteuser_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_remoteuser_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_remoteuser_user_permissions`
--

DROP TABLE IF EXISTS `accounts_remoteuser_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_remoteuser_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `remoteuser_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_remoteuser_user_pe_remoteuser_id_6011e6d52634e41d_uniq` (`remoteuser_id`,`permission_id`),
  KEY `accounts_remoteuser_user_permissions_29e729b2` (`remoteuser_id`),
  KEY `accounts_remoteuser_user_permissions_83d7f98b` (`permission_id`),
  CONSTRAINT `permission_id_refs_id_ef5b5870` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `remoteuser_id_refs_id_933fb045` FOREIGN KEY (`remoteuser_id`) REFERENCES `accounts_remoteuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_remoteuser_user_permissions`
--

LOCK TABLES `accounts_remoteuser_user_permissions` WRITE;
/*!40000 ALTER TABLE `accounts_remoteuser_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_remoteuser_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_useractivation`
--

DROP TABLE IF EXISTS `accounts_useractivation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_useractivation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `activation_key` varchar(40) NOT NULL,
  `task_key` varchar(40) NOT NULL,
  `first_name` varchar(40) NOT NULL,
  `last_name` varchar(40) NOT NULL,
  `email` varchar(254) NOT NULL,
  `company_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  UNIQUE KEY `activation_key` (`activation_key`),
  KEY `accounts_useractivation_af2d2943` (`task_key`)
) ENGINE=InnoDB AUTO_INCREMENT=111 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_useractivation`
--

LOCK TABLES `accounts_useractivation` WRITE;
/*!40000 ALTER TABLE `accounts_useractivation` DISABLE KEYS */;
INSERT INTO `accounts_useractivation` VALUES (1,13,'d52d6c764056fdae51003f9194716fe7f0586fc0','','N/A','N/A','N/A',0),(2,14,'98eafc7742147d5cc4c76b19a898d25ea514b07f','','N/A','N/A','N/A',0),(3,15,'c7c96ea3ba7df922e3af85ae4a3b68c971f29a25','','N/A','N/A','N/A',0),(4,16,'f1404c1a80c9fa6b5f71b88049e0ecca0fe7fdbf','','N/A','N/A','N/A',0),(5,17,'03aa03b355133a2d18e4acd64e8ceccf85046f32','','N/A','N/A','N/A',0),(6,18,'cce8e71192bf211fcc20785490b5a0499a5794f4','','N/A','N/A','N/A',0),(7,19,'fe83a2d82ce0c3702543a38946ce15c72d2e0143','','N/A','N/A','N/A',0),(8,20,'4f5b75fc81c3ee2286bf458962ae7cbcc2519464','','N/A','N/A','N/A',0),(9,21,'4be8b8e7b342eccf42cdcdf09a3fe1046810e687','','N/A','N/A','N/A',0),(10,22,'4d445eea5d70ea9d78863db6c890cfb05abc0f90','','N/A','N/A','N/A',0),(11,23,'3515b617803c5def0c2ad500ac02944e2c95be9f','','N/A','N/A','N/A',0),(12,24,'79f8446c333b15d43cf6b2fc2fb329b6944f4f46','','N/A','N/A','N/A',0),(13,25,'3be892005fe4a8ab66f0104d1451dbdc5b465b0d','','N/A','N/A','N/A',0),(14,26,'c5319137e987fbecf4371012ff0f77247cf17d3f','','N/A','N/A','N/A',0),(15,27,'101053a618d6decf8105772e6bc912acb8422c50','','N/A','N/A','N/A',0),(16,28,'d11fb06103d69e75de7d3aaca47bac409555ab8f','','N/A','N/A','N/A',0),(17,29,'6c18e1ffc96599bcb65d4ec9e5ead296bd2ebd88','','N/A','N/A','N/A',0),(18,30,'2be5f16cd808d3375f5fd7ea783780a9a1c981cc','','N/A','N/A','N/A',0),(19,31,'6df13d977829f4b778ffd124c899b3060b05f352','','N/A','N/A','N/A',0),(20,32,'f4cd4cb52eabaa88124a46079e7d4f6879d8772f','','N/A','N/A','N/A',0),(21,33,'b15b8a5eb7d1588efdeaba0b2c596d4298e82d24','','N/A','N/A','N/A',0),(22,34,'564e46fe85f71f2c01679223c6578590f85c69aa','','N/A','N/A','N/A',0),(23,35,'525db915fcbcd9feba182335530de9c49bcab7ac','','N/A','N/A','N/A',0),(24,36,'0105145254f6ad5196b448808a648eaa118403ee','','N/A','N/A','N/A',0),(25,37,'1ba5f1cb5e39c0685a4d9da32b90e39df4f308ad','','N/A','N/A','N/A',0),(26,38,'6e6ab34f7e959a8b557098b6151a6f83aece5ae0','','N/A','N/A','N/A',0),(27,39,'7084a072d5369fb892d1b5285b2ca82c89d313d6','','N/A','N/A','N/A',0),(28,40,'51f755347ca5677549f50a30fe8877deea23c41f','','N/A','N/A','N/A',0),(29,41,'8980cd7184ca8b6f36164096c52da9bc9b63ef3d','','N/A','N/A','N/A',0),(30,42,'888ac38d6e8370fcfbd8ff56c933e5ade2a2c5a8','','N/A','N/A','N/A',0),(31,43,'d3ea9467fcb53c61a76a4aeb93ab0921ec001f60','','N/A','N/A','N/A',0),(32,44,'e9d2556230b9ce6fc8d383118bb843da5ac93d8d','','N/A','N/A','N/A',0),(33,45,'523394587c53c1ea9af574781a0af5a73f401f46','','N/A','N/A','N/A',0),(34,46,'763fdc203cbd4f29e3fc28a812395db159063633','','N/A','N/A','N/A',0),(35,47,'3f092b9707ebe02f887299da96a3ffde75280e4b','','N/A','N/A','N/A',0),(36,48,'b37a22138651b825839e265cb8da9bc9ff780771','','N/A','N/A','N/A',0),(37,49,'5e06a1abfa8146c82cf458a747c3a89e68db17a6','','N/A','N/A','N/A',0),(38,50,'2384c98d13f5d2ca27a2ed2df945b30759f78b65','','N/A','N/A','N/A',0),(39,51,'313100d76dcd1c57b2ea88230b5aaa9bce8fa5e6','','N/A','N/A','N/A',0),(40,52,'3f40e2f1da92febd766c7bf2749360675f278615','','N/A','N/A','N/A',0),(41,53,'78ffc1c480f97c0a9eb6949c7615fc4c84acdb2d','','N/A','N/A','N/A',0),(42,54,'772ebe0c9fe264bfb256f99c73af280689c150ee','','N/A','N/A','N/A',0),(43,55,'7293948be30a74452d47d7daf862dfad03731fc0','','N/A','N/A','N/A',0),(44,56,'879056efe8c216b16a763b0e1763d7329772f1c3','','N/A','N/A','N/A',0),(45,57,'8bce8063c4ce54d25317b5023c14330287470df6','','N/A','N/A','N/A',0),(46,58,'6ce54e52a228ea31f0e3acc11b517451f8734ece','','N/A','N/A','N/A',0),(47,59,'d1a342257d5fc8e837aef96f8c0de829c0528c8d','','N/A','N/A','N/A',0),(48,60,'b57c26d918050815fbc7b4bb89a2db4f04a28ad6','','N/A','N/A','N/A',0),(49,61,'866f93a107b53f14545460343b35fca370b8ca1a','','N/A','N/A','N/A',0),(50,62,'2f91b48019b94e3ecad57b75e77f7aed3309b52a','','N/A','N/A','N/A',0),(51,63,'960fee6424bf5544d23404b11cc30d3887b86c85','','N/A','N/A','N/A',0),(52,64,'0197662cf8eceb0372604559462a1d40b3da3375','','N/A','N/A','N/A',0),(53,65,'be7556cb616944ad5a63fc73050d2856d4130050','','N/A','N/A','N/A',0),(54,66,'cd60eae837a1f50739365e29bee1106cd6e36935','','N/A','N/A','N/A',0),(55,67,'1ab8052e933e52a199a779038fcc03546f38975f','','N/A','N/A','N/A',0),(56,68,'e47f537e134c911bd4d840ff83b42ff7be646cd9','','N/A','N/A','N/A',0),(57,69,'a726c2a3c389e7f5ab9a58b59870aab589b4ff37','','N/A','N/A','N/A',0),(58,70,'d3bd897ccc4fd1b1edac18c2b7d61f9ed8028cfa','','N/A','N/A','N/A',0),(59,71,'72dbfd41cbf1d109b78d5992590d40d053b7e50a','','N/A','N/A','N/A',0),(60,72,'e96e98af66bf69bcfcbfcba58b29e9b2406a1f92','','N/A','N/A','N/A',0),(61,73,'1bc5bebc870a9e7fd7f06261b09a4afa510b41a3','','N/A','N/A','N/A',0),(62,74,'f99182b62417b96aba520c4047ee486cbd80ec10','','N/A','N/A','N/A',0),(63,75,'b39e9c3160c75086b2a829bd181a554131d6a5c8','','N/A','N/A','N/A',0),(64,76,'b2c874cd41b0dbfc195868b6c99c4aa06d4966aa','','N/A','N/A','N/A',0),(65,77,'348cb01381c8e13f60d2860761b191fbd421a01d','','N/A','N/A','N/A',0),(66,78,'6640280e6214b4e67c70a14804127bbe4ee64e33','','N/A','N/A','N/A',0),(67,79,'0783bd141daead4ee58344f89e7ee5f94b058b08','','N/A','N/A','N/A',0),(68,80,'da16212a8bdcf3280a533d1037aa84029c7f8a57','','N/A','N/A','N/A',0),(69,81,'4c90d1c19a46258b17a676c33e13ee15c9ce2f44','','N/A','N/A','N/A',0),(70,82,'ada6228853713ba5e167aaad0cda2484c0bf69da','','N/A','N/A','N/A',0),(71,83,'353ca8662d90dbc4daad01fa740812cd9c41e016','','N/A','N/A','N/A',0),(72,84,'75ac8e9e5e906199d31bc48b334dcb98cc70f390','','N/A','N/A','N/A',0),(73,85,'f1f4c78e7d3e71993d1f63dc1d2ea9f6be6af076','','N/A','N/A','N/A',0),(74,86,'76fd8066aec2b66d7ae9f5de5f142508fe2a0883','','N/A','N/A','N/A',0),(75,87,'2c83e4d2bf08c0ff63b8db0a1db13390f187d574','','N/A','N/A','N/A',0),(76,88,'7360d4342241daae26dcf7284d2d772aa6687057','','N/A','N/A','N/A',0),(77,89,'c19fbad15de05827a195f9a90592dc28c8e2503a','','N/A','N/A','N/A',0),(78,90,'33486db6d520e803f3f6b9fa30d97f8b1efea8f4','','N/A','N/A','N/A',0),(79,91,'4da5480c6b99f7789699aff3046e982e5da047bd','','N/A','N/A','N/A',0),(80,92,'2b7bdbea381fdacba0ff6e0d092856aa681583d1','','N/A','N/A','N/A',0),(81,93,'345ae19dc555c25af7fb72bf5d96a66372beb1df','','N/A','N/A','N/A',0),(82,94,'fc1974288571834c05a48bf96254c7f6a6b2580d','','N/A','N/A','N/A',0),(83,95,'512f6c8df51ba6165aa017eab2c587cee3456c3a','','N/A','N/A','N/A',0),(84,96,'ff49ae9cedcab7e6b59a644f0a78115021aa682b','','N/A','N/A','N/A',0),(85,97,'a9479b7ca26c686316fc073d7f0b1a625853e8f7','','N/A','N/A','N/A',0),(86,98,'ee030b18c24da941f395c96fd0a53d3804db3f8f','','N/A','N/A','N/A',0),(87,99,'023f43d5959109e6bad2f3adf3eb9b8b6e45b49e','','N/A','N/A','N/A',0),(88,100,'8b7962d53c93af6f57dc33e0fb2d81b934616ef1','','N/A','N/A','N/A',0),(89,101,'214a74bbd0ffe0015d50a75e4010a6961d5a4c1a','','N/A','N/A','N/A',0),(90,102,'efbf55ee6486ee11032f12716592c2d73bc89eb1','','N/A','N/A','N/A',0),(91,103,'1c380e75e5e8e87f329a2296632b374d1c5d9af8','','N/A','N/A','N/A',0),(92,104,'67127718f858e37e948b8dcb20241311a5d06363','','N/A','N/A','N/A',0),(93,105,'6d63f33763611b25ec5ffaab532dcbf0640117fa','','N/A','N/A','N/A',0),(94,106,'45d01fb37bddbed9e30b08296e9e61568ccc4441','','N/A','N/A','N/A',0),(95,107,'9a39a2f3e321300246128390e59f86d8fe1c7e55','','N/A','N/A','N/A',0),(96,108,'6ca3fd35aa0e46437c338e8f9422c3273f4f9b0d','','N/A','N/A','N/A',0),(97,109,'7fbfc5b0de54feeba92c0a75acb8311315cca8be','','N/A','N/A','N/A',0),(98,110,'8a90df8aa260b00372b32ad9f8723802d96f2325','','N/A','N/A','N/A',0),(99,111,'8fe2dc3ee50157e03ec2ec1a81023f0e103879fb','','N/A','N/A','N/A',0),(100,112,'f2007b8a79d1f2bf9189646d52d8076a1ca65cb8','','N/A','N/A','N/A',0),(101,113,'79db41c9f6edca1682c4a3f4efa6888ea2f90507','','N/A','N/A','N/A',0),(102,114,'1099a53cf5a4d10cca42b9a77b8670c54d53382d','','N/A','N/A','N/A',0),(103,115,'ca46244cdddeed3d1cb0711fe4218c79dbc78204','','N/A','N/A','N/A',0),(104,116,'cce12634aff8b450bb8e4208ba072e5f7c832089','','N/A','N/A','N/A',0),(105,117,'4a21a114cbac56ea3862a7018f6179f5b40d9c3a','','N/A','N/A','N/A',0),(106,118,'2f99908f8eefbb1999473a360af7a80f86251ba3','','N/A','N/A','N/A',0),(107,119,'ecea0e7354704a6c31435a036121a4c0527387ec','','N/A','N/A','N/A',0),(108,120,'23bf2721771b2e236b1bb3ed8dbeb81225de104f','','N/A','N/A','N/A',0),(109,121,'440085eb989ca12d905273e3dc0e15e51b4c472a','','N/A','N/A','N/A',0),(110,122,'defd9031fca5fd53c94c8aefc031f486b14137a6','','N/A','N/A','N/A',0);
/*!40000 ALTER TABLE `accounts_useractivation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_userpasswordreset`
--

DROP TABLE IF EXISTS `accounts_userpasswordreset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_userpasswordreset` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `validation_key` varchar(40) NOT NULL,
  `time_requested` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  UNIQUE KEY `validation_key` (`validation_key`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_userpasswordreset`
--

LOCK TABLES `accounts_userpasswordreset` WRITE;
/*!40000 ALTER TABLE `accounts_userpasswordreset` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_userpasswordreset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_apros_accesskey`
--

DROP TABLE IF EXISTS `admin_apros_accesskey`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_apros_accesskey` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  `client_id` int(11) NOT NULL,
  `course_id` varchar(200) NOT NULL,
  `program_id` int(11) DEFAULT NULL,
  `name` varchar(200) NOT NULL,
  `disabled` tinyint(1) NOT NULL,
  `expiration_date` datetime DEFAULT NULL,
  `user_count` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_apros_accesskey`
--

LOCK TABLES `admin_apros_accesskey` WRITE;
/*!40000 ALTER TABLE `admin_apros_accesskey` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_apros_accesskey` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_apros_batchoperationerrors`
--

DROP TABLE IF EXISTS `admin_apros_batchoperationerrors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_apros_batchoperationerrors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task_key` varchar(40) NOT NULL,
  `error` longtext NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_batchoperationerrors_af2d2943` (`task_key`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_apros_batchoperationerrors`
--

LOCK TABLES `admin_apros_batchoperationerrors` WRITE;
/*!40000 ALTER TABLE `admin_apros_batchoperationerrors` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_apros_batchoperationerrors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_apros_batchoperationstatus`
--

DROP TABLE IF EXISTS `admin_apros_batchoperationstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_apros_batchoperationstatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task_key` varchar(40) NOT NULL,
  `attempted` int(11) NOT NULL,
  `failed` int(11) NOT NULL,
  `succeded` int(11) NOT NULL,
  `time_requested` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `task_key` (`task_key`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_apros_batchoperationstatus`
--

LOCK TABLES `admin_apros_batchoperationstatus` WRITE;
/*!40000 ALTER TABLE `admin_apros_batchoperationstatus` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_apros_batchoperationstatus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_apros_brandingsettings`
--

DROP TABLE IF EXISTS `admin_apros_brandingsettings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_apros_brandingsettings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `background_image` varchar(100) NOT NULL,
  `logo_image` varchar(100) NOT NULL,
  `client_id` int(11) NOT NULL,
  `icon_color` varchar(20) NOT NULL,
  `background_color` varchar(20) NOT NULL,
  `background_style` varchar(1) NOT NULL,
  `rule_color` varchar(20) NOT NULL,
  `discover_title_color` varchar(20) NOT NULL,
  `discover_author_color` varchar(20) NOT NULL,
  `discover_rule_color` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `client_id` (`client_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_apros_brandingsettings`
--

LOCK TABLES `admin_apros_brandingsettings` WRITE;
/*!40000 ALTER TABLE `admin_apros_brandingsettings` DISABLE KEYS */;
INSERT INTO `admin_apros_brandingsettings` VALUES (2,'','images/learner_dashboard/branding/logos/Screen_Shot_2016-04-12_at_12.46.21.png',1,'#9af23e','#2c59ed','2','#00f8bd','#e364ff','#f43b3f','#80f11e');
/*!40000 ALTER TABLE `admin_apros_brandingsettings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_apros_clientcustomization`
--

DROP TABLE IF EXISTS `admin_apros_clientcustomization`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_apros_clientcustomization` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `client_id` int(11) NOT NULL,
  `hex_notification` varchar(7) NOT NULL,
  `hex_background_bar` varchar(7) NOT NULL,
  `hex_program_name` varchar(7) NOT NULL,
  `hex_navigation_icons` varchar(7) NOT NULL,
  `hex_course_title` varchar(7) NOT NULL,
  `hex_page_background` varchar(7) NOT NULL,
  `client_logo` varchar(200) NOT NULL,
  `hex_notification_text` varchar(7) NOT NULL,
  `identity_provider` varchar(200) NOT NULL,
  `client_background` varchar(200) NOT NULL,
  `client_background_css` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `client_id` (`client_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_apros_clientcustomization`
--

LOCK TABLES `admin_apros_clientcustomization` WRITE;
/*!40000 ALTER TABLE `admin_apros_clientcustomization` DISABLE KEYS */;
INSERT INTO `admin_apros_clientcustomization` VALUES (1,2,'','','','','','','','','dsa','',''),(2,3,'','','','','','','','','Test1','',''),(3,4,'','','','','','','','','dsa','',''),(4,5,'','','','','','','','','dsa','',''),(5,6,'','','','','','','','','dsa','',''),(6,1,'','','','','','','/accounts/images/client_logo-1-1462799349.png','','','','');
/*!40000 ALTER TABLE `admin_apros_clientcustomization` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_apros_clientnavlinks`
--

DROP TABLE IF EXISTS `admin_apros_clientnavlinks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_apros_clientnavlinks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `client_id` int(11) NOT NULL,
  `link_name` varchar(200) NOT NULL,
  `link_label` varchar(200) NOT NULL,
  `link_url` varchar(200) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `admin_clientnavlinks_client_id_ee6f8e86f65c43e_uniq` (`client_id`,`link_name`),
  KEY `admin_clientnavlinks_bc33a32b` (`client_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_apros_clientnavlinks`
--

LOCK TABLES `admin_apros_clientnavlinks` WRITE;
/*!40000 ALTER TABLE `admin_apros_clientnavlinks` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_apros_clientnavlinks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_apros_companycontact`
--

DROP TABLE IF EXISTS `admin_apros_companycontact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_apros_companycontact` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `company_id` int(11) NOT NULL,
  `contact_type` varchar(1) NOT NULL,
  `full_name` varchar(200) NOT NULL,
  `title` varchar(200) NOT NULL,
  `email` varchar(200) NOT NULL,
  `phone` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `admin_companycontact_company_id_52106804c99c5213_uniq` (`company_id`,`contact_type`),
  KEY `admin_companycontact_3569a607` (`company_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_apros_companycontact`
--

LOCK TABLES `admin_apros_companycontact` WRITE;
/*!40000 ALTER TABLE `admin_apros_companycontact` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_apros_companycontact` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_apros_companyinvoicingdetails`
--

DROP TABLE IF EXISTS `admin_apros_companyinvoicingdetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_apros_companyinvoicingdetails` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `company_id` int(11) NOT NULL,
  `full_name` varchar(200) NOT NULL,
  `title` varchar(200) NOT NULL,
  `address1` varchar(200) NOT NULL,
  `address2` varchar(200) NOT NULL,
  `city` varchar(200) NOT NULL,
  `state` varchar(200) NOT NULL,
  `postal_code` varchar(200) NOT NULL,
  `country` varchar(200) NOT NULL,
  `po` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `company_id` (`company_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_apros_companyinvoicingdetails`
--

LOCK TABLES `admin_apros_companyinvoicingdetails` WRITE;
/*!40000 ALTER TABLE `admin_apros_companyinvoicingdetails` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_apros_companyinvoicingdetails` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_apros_dashboardadminquickfilter`
--

DROP TABLE IF EXISTS `admin_apros_dashboardadminquickfilter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_apros_dashboardadminquickfilter` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date_created` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `program_id` int(11) NOT NULL,
  `course_id` varchar(200) DEFAULT NULL,
  `company_id` int(11) DEFAULT NULL,
  `group_work_project_id` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_dashboardadminquickfilter_816e0180` (`date_created`),
  KEY `admin_dashboardadminquickfilter_1ffdedc6` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_apros_dashboardadminquickfilter`
--

LOCK TABLES `admin_apros_dashboardadminquickfilter` WRITE;
/*!40000 ALTER TABLE `admin_apros_dashboardadminquickfilter` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_apros_dashboardadminquickfilter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_apros_emailtemplate`
--

DROP TABLE IF EXISTS `admin_apros_emailtemplate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_apros_emailtemplate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(64) NOT NULL,
  `subject` varchar(256) NOT NULL,
  `body` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_apros_emailtemplate`
--

LOCK TABLES `admin_apros_emailtemplate` WRITE;
/*!40000 ALTER TABLE `admin_apros_emailtemplate` DISABLE KEYS */;
INSERT INTO `admin_apros_emailtemplate` VALUES (1,'s13123','4232432','No1123232331ne'),(2,'None','None','None');
/*!40000 ALTER TABLE `admin_apros_emailtemplate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_apros_learnerdashboard`
--

DROP TABLE IF EXISTS `admin_apros_learnerdashboard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_apros_learnerdashboard` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(80) NOT NULL,
  `description` varchar(5000) NOT NULL,
  `client_id` int(11) NOT NULL,
  `course_id` varchar(500) NOT NULL,
  `title_color` varchar(20) NOT NULL,
  `description_color` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `client_id` (`client_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_apros_learnerdashboard`
--

LOCK TABLES `admin_apros_learnerdashboard` WRITE;
/*!40000 ALTER TABLE `admin_apros_learnerdashboard` DISABLE KEYS */;
INSERT INTO `admin_apros_learnerdashboard` VALUES (1,'TEst',' Test1dddddasdfds d sfd df df Test1dddddasdfds d sfd df df Test1dddddasdfds d sfd df df Test1dddddasdfds d sfd df df vTest1dddddasdfds d sfd df df vTest1dddddasdfds d sfd df df Test1dddddasdfds d sfd df df Test1dddddasdfds d sfd df dfasd',1,'course-v1:edX+DemoX+Demo_Course','#0af5fc','#00f620'),(2,'','',2,'course-v1:edX+DemoX+Demo_Course','#FFFFFF','#FFFFFF'),(3,'Test5','dsadsadas',3,'course-v1:edX+DemoX+Demo_Course','#FFFFFF','#FFFFFF'),(4,'Test za bez LD flaga','',5,'Test1/Test1/Test1','#FFFFFF','#FFFFFF');
/*!40000 ALTER TABLE `admin_apros_learnerdashboard` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_apros_learnerdashboarddiscovery`
--

DROP TABLE IF EXISTS `admin_apros_learnerdashboarddiscovery`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_apros_learnerdashboarddiscovery` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `link` varchar(5000) DEFAULT NULL,
  `title` varchar(5000),
  `author` varchar(5000),
  `learner_dashboard_id` int(11) NOT NULL,
  `position` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_learnerdashboarddiscovery_05ce392f` (`learner_dashboard_id`),
  CONSTRAINT `learner_dashboard_id_refs_id_23674eed` FOREIGN KEY (`learner_dashboard_id`) REFERENCES `admin_apros_learnerdashboard` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_apros_learnerdashboarddiscovery`
--

LOCK TABLES `admin_apros_learnerdashboarddiscovery` WRITE;
/*!40000 ALTER TABLE `admin_apros_learnerdashboarddiscovery` DISABLE KEYS */;
INSERT INTO `admin_apros_learnerdashboarddiscovery` VALUES (1,'http://apros.mcka.local:8080/admin/client-admin/1/courses/course-v1:edX+DemoX+De','Test1','',1,1),(2,'http://apros.mcka.local:8080/admin/client-admin/1/courses/course-v1:edX+DemoX+De','Test122','',1,0),(3,'http://apros.mcka.local:8080/admin/client-admin/1/courses/course-v1:edX+DemoX+Demo_Course/learner_dashboard/discover/list','Test1','sadas',1,100);
/*!40000 ALTER TABLE `admin_apros_learnerdashboarddiscovery` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_apros_learnerdashboardmilestone`
--

DROP TABLE IF EXISTS `admin_apros_learnerdashboardmilestone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_apros_learnerdashboardmilestone` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `label` varchar(20) NOT NULL,
  `title` varchar(5000) NOT NULL,
  `location` varchar(250) NOT NULL,
  `details` varchar(5000) NOT NULL,
  `download_link` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `start_date` datetime(6) DEFAULT NULL,
  `end_date` datetime(6) DEFAULT NULL,
  `active` tinyint(1) NOT NULL,
  `milestone_type` varchar(1) NOT NULL,
  `digital_content_type` varchar(1) NOT NULL,
  `learner_dashboard_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `D9be26980654a54eae4c8d324d81e648` (`learner_dashboard_id`),
  CONSTRAINT `D9be26980654a54eae4c8d324d81e648` FOREIGN KEY (`learner_dashboard_id`) REFERENCES `admin_apros_learnerdashboard` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_apros_learnerdashboardmilestone`
--

LOCK TABLES `admin_apros_learnerdashboardmilestone` WRITE;
/*!40000 ALTER TABLE `admin_apros_learnerdashboardmilestone` DISABLE KEYS */;
INSERT INTO `admin_apros_learnerdashboardmilestone` VALUES (1,'2112','132','312','','','',NULL,NULL,0,'3','',1),(2,'1111231231','1231231','123123','','','',NULL,NULL,0,'3','2',1);
/*!40000 ALTER TABLE `admin_apros_learnerdashboardmilestone` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_apros_learnerdashboardmilestoneprogress`
--

DROP TABLE IF EXISTS `admin_apros_learnerdashboardmilestoneprogress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_apros_learnerdashboardmilestoneprogress` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` int(11) NOT NULL,
  `progress` varchar(1) NOT NULL,
  `percentage` int(11) NOT NULL,
  `milestone_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user` (`user`),
  UNIQUE KEY `percentage` (`percentage`),
  KEY `D3b6893ed7d021009ba5b1b5f2257ad8` (`milestone_id`),
  CONSTRAINT `D3b6893ed7d021009ba5b1b5f2257ad8` FOREIGN KEY (`milestone_id`) REFERENCES `admin_apros_learnerdashboardmilestone` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_apros_learnerdashboardmilestoneprogress`
--

LOCK TABLES `admin_apros_learnerdashboardmilestoneprogress` WRITE;
/*!40000 ALTER TABLE `admin_apros_learnerdashboardmilestoneprogress` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_apros_learnerdashboardmilestoneprogress` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_apros_learnerdashboardtile`
--

DROP TABLE IF EXISTS `admin_apros_learnerdashboardtile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_apros_learnerdashboardtile` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(40) NOT NULL,
  `link` varchar(500) NOT NULL,
  `background_image` varchar(100) NOT NULL,
  `tile_type` varchar(1) NOT NULL,
  `learner_dashboard_id` int(11) NOT NULL,
  `position` int(11) NOT NULL,
  `title_color` varchar(20) NOT NULL,
  `tile_background_color` varchar(20) NOT NULL,
  `label` varchar(20) NOT NULL,
  `note` varchar(40) NOT NULL,
  `label_color` varchar(20) NOT NULL,
  `note_color` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_learnerdashboardtile_05ce392f` (`learner_dashboard_id`),
  CONSTRAINT `learner_dashboard_id_refs_id_5a95608e` FOREIGN KEY (`learner_dashboard_id`) REFERENCES `admin_apros_learnerdashboard` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_apros_learnerdashboardtile`
--

LOCK TABLES `admin_apros_learnerdashboardtile` WRITE;
/*!40000 ALTER TABLE `admin_apros_learnerdashboardtile` DISABLE KEYS */;
INSERT INTO `admin_apros_learnerdashboardtile` VALUES (23,'Test2','http://apros.mcka.local:8080/admin/client-admin/1/courses/course-v1:edX+DemoX+De','','3',2,1,'#000000','#FFFFFF','','','#000000','#868685'),(24,'TEst5','Test1','','3',2,0,'#000000','#FFFFFF','','','#000000','#868685'),(25,'Test1','Test1','','3',3,100,'#000000','#FFFFFF','','','#000000','#868685'),(29,'32','/learnerdashboardhttp://apros.mcka.local:8080/admin/client-admin/1/courses/course-v1:edX+DemoX+De/lesson','','2',1,1,'#3384ca','#ffffff','23','32','#000000','#868685'),(30,'1','/learnerdashboard','','2',1,0,'#3384ca','#ffffff','111','23','#000000','#868685'),(31,'Test1','/learnerdashboardhttp://apros.mcka.local:8080/admin/client-admin/1/courses/course-v1:edX+DemoX+De/lesson','','2',1,100,'#3384ca','#ffffff','Test1','TEst4','#000000','#868685'),(32,'Test2','Test1','','1',1,100,'#3384ca','#ffffff','Test5','asdasdas','#000000','#868685'),(33,'','/learnerdashboardTest1/module/','','3',1,100,'#3384ca','#ffffff','sadd','','#000000','#868685'),(34,'','/learnerdashboardTest1/lesson','','2',1,100,'#3384ca','#ffffff','Test1','','#000000','#868685'),(35,'123','/learnerdashboard23/lesson','','2',1,100,'#3384ca','#ffffff','321','','#000000','#868685'),(36,'','/learnerdashboard132/lesson','','2',1,100,'#3384ca','#ffffff','13312','','#000000','#868685'),(37,'','/courses/333','','4',1,100,'#3384ca','#ffffff','3333','','#000000','#868685'),(38,'','/learnerdashboardhttp://apros.mcka.local:8080/admin/client-admin/1/courses/course-v1:edX+DemoX+De/lesson','','2',1,100,'#3384ca','#ffffff','Test1','','#000000','#868685');
/*!40000 ALTER TABLE `admin_apros_learnerdashboardtile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_apros_tilebookmark`
--

DROP TABLE IF EXISTS `admin_apros_tilebookmark`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_apros_tilebookmark` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` int(11) NOT NULL,
  `lesson_link` varchar(2000) DEFAULT NULL,
  `tile_id` int(11) NOT NULL,
  `learner_dashboard_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user` (`user`),
  KEY `admin_tilebookmark_923f1dcd` (`tile_id`),
  KEY `admin_tilebookmark_05ce392f` (`learner_dashboard_id`),
  CONSTRAINT `learner_dashboard_id_refs_id_23828b90` FOREIGN KEY (`learner_dashboard_id`) REFERENCES `admin_apros_learnerdashboard` (`id`),
  CONSTRAINT `tile_id_refs_id_cbd5d1a0` FOREIGN KEY (`tile_id`) REFERENCES `admin_apros_learnerdashboardtile` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_apros_tilebookmark`
--

LOCK TABLES `admin_apros_tilebookmark` WRITE;
/*!40000 ALTER TABLE `admin_apros_tilebookmark` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_apros_tilebookmark` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_apros_userregistrationbatch`
--

DROP TABLE IF EXISTS `admin_apros_userregistrationbatch`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_apros_userregistrationbatch` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task_key` varchar(40) NOT NULL,
  `attempted` int(11) NOT NULL,
  `failed` int(11) NOT NULL,
  `succeded` int(11) NOT NULL,
  `time_requested` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `task_key` (`task_key`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_apros_userregistrationbatch`
--

LOCK TABLES `admin_apros_userregistrationbatch` WRITE;
/*!40000 ALTER TABLE `admin_apros_userregistrationbatch` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_apros_userregistrationbatch` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_apros_userregistrationerror`
--

DROP TABLE IF EXISTS `admin_apros_userregistrationerror`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_apros_userregistrationerror` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task_key` varchar(40) NOT NULL,
  `error` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_userregistrationerror_af2d2943` (`task_key`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_apros_userregistrationerror`
--

LOCK TABLES `admin_apros_userregistrationerror` WRITE;
/*!40000 ALTER TABLE `admin_apros_userregistrationerror` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_apros_userregistrationerror` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_5f412f9a` (`group_id`),
  KEY `auth_group_permissions_83d7f98b` (`permission_id`),
  CONSTRAINT `group_id_refs_id_f4b32aac` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `permission_id_refs_id_6ba0f519` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  KEY `auth_permission_37ef4eb4` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_d043b34a` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=169 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add permission',1,'add_permission'),(2,'Can change permission',1,'change_permission'),(3,'Can delete permission',1,'delete_permission'),(4,'Can add group',2,'add_group'),(5,'Can change group',2,'change_group'),(6,'Can delete group',2,'delete_group'),(7,'Can add content type',3,'add_contenttype'),(8,'Can change content type',3,'change_contenttype'),(9,'Can delete content type',3,'delete_contenttype'),(10,'Can add session',4,'add_session'),(11,'Can change session',4,'change_session'),(12,'Can delete session',4,'delete_session'),(13,'Can add migration history',5,'add_migrationhistory'),(14,'Can change migration history',5,'change_migrationhistory'),(15,'Can delete migration history',5,'delete_migrationhistory'),(19,'Can add user registration error',7,'add_userregistrationerror'),(20,'Can change user registration error',7,'change_userregistrationerror'),(21,'Can delete user registration error',7,'delete_userregistrationerror'),(22,'Can add user registration batch',8,'add_userregistrationbatch'),(23,'Can change user registration batch',8,'change_userregistrationbatch'),(24,'Can delete user registration batch',8,'delete_userregistrationbatch'),(25,'Can add client nav links',9,'add_clientnavlinks'),(26,'Can change client nav links',9,'change_clientnavlinks'),(27,'Can delete client nav links',9,'delete_clientnavlinks'),(28,'Can add client customization',10,'add_clientcustomization'),(29,'Can change client customization',10,'change_clientcustomization'),(30,'Can delete client customization',10,'delete_clientcustomization'),(31,'Can add access key',11,'add_accesskey'),(32,'Can change access key',11,'change_accesskey'),(33,'Can delete access key',11,'delete_accesskey'),(34,'Can add dashboard admin quick filter',12,'add_dashboardadminquickfilter'),(35,'Can change dashboard admin quick filter',12,'change_dashboardadminquickfilter'),(36,'Can delete dashboard admin quick filter',12,'delete_dashboardadminquickfilter'),(37,'Can add user',13,'add_remoteuser'),(38,'Can change user',13,'change_remoteuser'),(39,'Can delete user',13,'delete_remoteuser'),(40,'Can add user activation',14,'add_useractivation'),(41,'Can change user activation',14,'change_useractivation'),(42,'Can delete user activation',14,'delete_useractivation'),(43,'Can add user password reset',15,'add_userpasswordreset'),(44,'Can change user password reset',15,'change_userpasswordreset'),(45,'Can delete user password reset',15,'delete_userpasswordreset'),(46,'Can add curated content item',16,'add_curatedcontentitem'),(47,'Can change curated content item',16,'change_curatedcontentitem'),(48,'Can delete curated content item',16,'delete_curatedcontentitem'),(49,'Can add lesson notes item',17,'add_lessonnotesitem'),(50,'Can change lesson notes item',17,'change_lessonnotesitem'),(51,'Can delete lesson notes item',17,'delete_lessonnotesitem'),(52,'Can add feature flags',18,'add_featureflags'),(53,'Can change feature flags',18,'change_featureflags'),(54,'Can delete feature flags',18,'delete_featureflags'),(55,'Can add license grant',19,'add_licensegrant'),(56,'Can change license grant',19,'change_licensegrant'),(57,'Can delete license grant',19,'delete_licensegrant'),(58,'Can add api token',20,'add_apitoken'),(59,'Can change api token',20,'change_apitoken'),(60,'Can delete api token',20,'delete_apitoken'),(61,'Can add batch operation errors',21,'add_batchoperationerrors'),(62,'Can change batch operation errors',21,'change_batchoperationerrors'),(63,'Can delete batch operation errors',21,'delete_batchoperationerrors'),(64,'Can add batch operation status',22,'add_batchoperationstatus'),(65,'Can change batch operation status',22,'change_batchoperationstatus'),(66,'Can delete batch operation status',22,'delete_batchoperationstatus'),(67,'Can add branding settings',23,'add_brandingsettings'),(68,'Can change branding settings',23,'change_brandingsettings'),(69,'Can delete branding settings',23,'delete_brandingsettings'),(82,'Can add learner dashboard',28,'add_learnerdashboard'),(83,'Can change learner dashboard',28,'change_learnerdashboard'),(84,'Can delete learner dashboard',28,'delete_learnerdashboard'),(85,'Can add learner dashboard tile',29,'add_learnerdashboardtile'),(86,'Can change learner dashboard tile',29,'change_learnerdashboardtile'),(87,'Can delete learner dashboard tile',29,'delete_learnerdashboardtile'),(88,'Can add learner dashboard discovery',30,'add_learnerdashboarddiscovery'),(89,'Can change learner dashboard discovery',30,'change_learnerdashboarddiscovery'),(90,'Can delete learner dashboard discovery',30,'delete_learnerdashboarddiscovery'),(91,'Can add learner dashboard resource',31,'add_learnerdashboardresource'),(92,'Can change learner dashboard resource',31,'change_learnerdashboardresource'),(93,'Can delete learner dashboard resource',31,'delete_learnerdashboardresource'),(94,'Can add log entry',32,'add_logentry'),(95,'Can change log entry',32,'change_logentry'),(96,'Can delete log entry',32,'delete_logentry'),(97,'Can add email template',33,'add_emailtemplate'),(98,'Can change email template',33,'change_emailtemplate'),(99,'Can delete email template',33,'delete_emailtemplate'),(100,'Can add company invoicing details',34,'add_companyinvoicingdetails'),(101,'Can change company invoicing details',34,'change_companyinvoicingdetails'),(102,'Can delete company invoicing details',34,'delete_companyinvoicingdetails'),(103,'Can add company contact',35,'add_companycontact'),(104,'Can change company contact',35,'change_companycontact'),(105,'Can delete company contact',35,'delete_companycontact'),(106,'Can add tile bookmark',36,'add_tilebookmark'),(107,'Can change tile bookmark',36,'change_tilebookmark'),(108,'Can delete tile bookmark',36,'delete_tilebookmark'),(109,'Can add user registration error',37,'add_userregistrationerror'),(110,'Can change user registration error',37,'change_userregistrationerror'),(111,'Can delete user registration error',37,'delete_userregistrationerror'),(112,'Can add user registration batch',38,'add_userregistrationbatch'),(113,'Can change user registration batch',38,'change_userregistrationbatch'),(114,'Can delete user registration batch',38,'delete_userregistrationbatch'),(115,'Can add batch operation errors',39,'add_batchoperationerrors'),(116,'Can change batch operation errors',39,'change_batchoperationerrors'),(117,'Can delete batch operation errors',39,'delete_batchoperationerrors'),(118,'Can add batch operation status',40,'add_batchoperationstatus'),(119,'Can change batch operation status',40,'change_batchoperationstatus'),(120,'Can delete batch operation status',40,'delete_batchoperationstatus'),(121,'Can add client nav links',41,'add_clientnavlinks'),(122,'Can change client nav links',41,'change_clientnavlinks'),(123,'Can delete client nav links',41,'delete_clientnavlinks'),(124,'Can add client customization',42,'add_clientcustomization'),(125,'Can change client customization',42,'change_clientcustomization'),(126,'Can delete client customization',42,'delete_clientcustomization'),(127,'Can add company invoicing details',43,'add_companyinvoicingdetails'),(128,'Can change company invoicing details',43,'change_companyinvoicingdetails'),(129,'Can delete company invoicing details',43,'delete_companyinvoicingdetails'),(130,'Can add company contact',44,'add_companycontact'),(131,'Can change company contact',44,'change_companycontact'),(132,'Can delete company contact',44,'delete_companycontact'),(133,'Can add access key',45,'add_accesskey'),(134,'Can change access key',45,'change_accesskey'),(135,'Can delete access key',45,'delete_accesskey'),(136,'Can add dashboard admin quick filter',46,'add_dashboardadminquickfilter'),(137,'Can change dashboard admin quick filter',46,'change_dashboardadminquickfilter'),(138,'Can delete dashboard admin quick filter',46,'delete_dashboardadminquickfilter'),(139,'Can add branding settings',47,'add_brandingsettings'),(140,'Can change branding settings',47,'change_brandingsettings'),(141,'Can delete branding settings',47,'delete_brandingsettings'),(142,'Can add learner dashboard',48,'add_learnerdashboard'),(143,'Can change learner dashboard',48,'change_learnerdashboard'),(144,'Can delete learner dashboard',48,'delete_learnerdashboard'),(145,'Can add learner dashboard tile',49,'add_learnerdashboardtile'),(146,'Can change learner dashboard tile',49,'change_learnerdashboardtile'),(147,'Can delete learner dashboard tile',49,'delete_learnerdashboardtile'),(148,'Can add learner dashboard discovery',50,'add_learnerdashboarddiscovery'),(149,'Can change learner dashboard discovery',50,'change_learnerdashboarddiscovery'),(150,'Can delete learner dashboard discovery',50,'delete_learnerdashboarddiscovery'),(151,'Can add email template',51,'add_emailtemplate'),(152,'Can change email template',51,'change_emailtemplate'),(153,'Can delete email template',51,'delete_emailtemplate'),(154,'Can add tile bookmark',52,'add_tilebookmark'),(155,'Can change tile bookmark',52,'change_tilebookmark'),(156,'Can delete tile bookmark',52,'delete_tilebookmark'),(157,'Can add user test',53,'add_usertest'),(158,'Can change user test',53,'change_usertest'),(159,'Can delete user test',53,'delete_usertest'),(160,'Can add session test',54,'add_sessiontest'),(161,'Can change session test',54,'change_sessiontest'),(162,'Can delete session test',54,'delete_sessiontest'),(163,'Can add learner dashboard milestone',55,'add_learnerdashboardmilestone'),(164,'Can change learner dashboard milestone',55,'change_learnerdashboardmilestone'),(165,'Can delete learner dashboard milestone',55,'delete_learnerdashboardmilestone'),(166,'Can add learner dashboard milestone progress',56,'add_learnerdashboardmilestoneprogress'),(167,'Can change learner dashboard milestone progress',56,'change_learnerdashboardmilestoneprogress'),(168,'Can delete learner dashboard milestone progress',56,'delete_learnerdashboardmilestoneprogress');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courses_featureflags`
--

DROP TABLE IF EXISTS `courses_featureflags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `courses_featureflags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `course_id` varchar(200) NOT NULL,
  `group_work` tinyint(1) NOT NULL,
  `discussions` tinyint(1) NOT NULL,
  `cohort_map` tinyint(1) NOT NULL,
  `proficiency` tinyint(1) NOT NULL,
  `learner_dashboard` tinyint(1) NOT NULL,
  `progress_page` tinyint(1) NOT NULL,
  `notifications` tinyint(1) NOT NULL,
  `branding` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `courses_featureflags_064a9e9c` (`course_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses_featureflags`
--

LOCK TABLES `courses_featureflags` WRITE;
/*!40000 ALTER TABLE `courses_featureflags` DISABLE KEYS */;
INSERT INTO `courses_featureflags` VALUES (1,'course-v1:edX+DemoX+Demo_Course',1,1,1,1,1,1,1,1),(2,'Test1/Test1/Test1',1,1,1,1,1,1,1,1);
/*!40000 ALTER TABLE `courses_featureflags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courses_lessonnotesitem`
--

DROP TABLE IF EXISTS `courses_lessonnotesitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `courses_lessonnotesitem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `body` longtext NOT NULL,
  `course_id` varchar(200) NOT NULL,
  `lesson_id` varchar(200) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `user_id` int(11),
  `module_id` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `courses_lessonnotesitem_064a9e9c` (`course_id`),
  KEY `courses_lessonnotesitem_08a52a00` (`lesson_id`),
  KEY `courses_lessonnotesitem_1ffdedc6` (`user_id`),
  KEY `courses_lessonnotesitem_6450dfde` (`module_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses_lessonnotesitem`
--

LOCK TABLES `courses_lessonnotesitem` WRITE;
/*!40000 ALTER TABLE `courses_lessonnotesitem` DISABLE KEYS */;
/*!40000 ALTER TABLE `courses_lessonnotesitem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `curated_content_item`
--

DROP TABLE IF EXISTS `curated_content_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curated_content_item` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `body` varchar(1000) DEFAULT NULL,
  `byline` varchar(255) DEFAULT NULL,
  `url` varchar(200) DEFAULT NULL,
  `image_url` varchar(200) DEFAULT NULL,
  `content_type` varchar(3) NOT NULL,
  `sequence` int(11) NOT NULL,
  `twitter_username` varchar(255),
  `thumbnail_url` varchar(200),
  `source` varchar(255),
  `byline_title` varchar(255),
  `created_at` datetime,
  `display_date` datetime,
  `course_id` varchar(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `curated_content_item`
--

LOCK TABLES `curated_content_item` WRITE;
/*!40000 ALTER TABLE `curated_content_item` DISABLE KEYS */;
INSERT INTO `curated_content_item` VALUES (1,'This is an Article','Here is the blurb!','','http://www.google.com','','art',1,'','','Harvard Business Review','','2013-03-16 17:41:28','2013-03-16 17:41:28','AndyU/au101/2014'),(2,'Performance and Problem Solving','Here is the blurb!','','http://www.google.com','','art',2,'','','McKinsey Insights','','2013-03-16 17:41:28','2013-03-16 17:41:28','AndyU/au101/2014'),(3,'The 4 Most Effective Ways Leaders Solve Problems','Here is the blurb!','','http://www.google.com','','art',3,'','','Forbes','','2013-03-16 17:41:28','2013-03-16 17:41:28','AndyU/au101/2014'),(4,'This is a Video, and Here is it\'s Title','This is a cool video about stuff that is fast and curious','','http://www.ted.com/talks/christopher_emdin_teach_teachers_how_to_create_magic','','vid',4,'',NULL,'TED Talks','','2013-03-16 17:41:28','2013-03-16 17:41:28','AndyU/au101/2014'),(5,'','This is a fine, fine tweet. Wow, it\'s good.','','','','twt',5,'tivs','','','','2013-03-16 17:41:28','2013-03-16 17:41:28','AndyU/au101/2014'),(6,'','If I had an hour to solve a problem I\'d spend 55 minutes thinking about the problem and 5 minutes thinking about solutions.','Albert Einstein','','http://placekitten.com/200/300','quo',6,'','',NULL,'Respectable Scientist','2013-03-16 17:41:28','2013-03-16 17:41:28','AndyU/au101/2014'),(7,'This is Also a Video with Some Key Insights','Scientists say the outer core is made mostly of iron and nickel. Iron and nickel are two important metals found everywhere on the planet.','','https://www.youtube.com/watch?v=duKL2dAJN6I','','vid',7,'','https://i1.ytimg.com/vi/duKL2dAJN6I/mqdefault.jpg','Center For Awesome Video','','2013-03-16 17:41:28','2013-03-16 17:41:28','AndyU/au101/2014'),(8,'This is an Infographic that links out.','','TED Talks','http://www.happify.com/hd/the-science-behind-a-happy-relationship/','','img',8,'','https://s3.amazonaws.com/happify-marty-prod-user-uploads/the-science-of-happy.png','','','2013-03-16 17:41:28','2013-03-16 17:41:28','AndyU/au101/2014'),(9,'','','','','','txt',10,'aaaa','','','',NULL,NULL,'course-v1:edX+DemoX+Demo_Course');
/*!40000 ALTER TABLE `curated_content_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `djang_content_type_id_697914295151027a_fk_django_content_type_id` (`content_type_id`),
  KEY `django_admin__user_id_52fdd58701c5f563_fk_accounts_remoteuser_id` (`user_id`),
  CONSTRAINT `djang_content_type_id_697914295151027a_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin__user_id_52fdd58701c5f563_fk_accounts_remoteuser_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_remoteuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_label` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (13,'accounts','remoteuser'),(14,'accounts','useractivation'),(15,'accounts','userpasswordreset'),(11,'admin','accesskey'),(21,'admin','batchoperationerrors'),(22,'admin','batchoperationstatus'),(23,'admin','brandingsettings'),(10,'admin','clientcustomization'),(9,'admin','clientnavlinks'),(35,'admin','companycontact'),(34,'admin','companyinvoicingdetails'),(12,'admin','dashboardadminquickfilter'),(33,'admin','emailtemplate'),(28,'admin','learnerdashboard'),(30,'admin','learnerdashboarddiscovery'),(31,'admin','learnerdashboardresource'),(29,'admin','learnerdashboardtile'),(32,'admin','logentry'),(36,'admin','tilebookmark'),(8,'admin','userregistrationbatch'),(7,'admin','userregistrationerror'),(45,'admin_apros','accesskey'),(39,'admin_apros','batchoperationerrors'),(40,'admin_apros','batchoperationstatus'),(47,'admin_apros','brandingsettings'),(42,'admin_apros','clientcustomization'),(41,'admin_apros','clientnavlinks'),(44,'admin_apros','companycontact'),(43,'admin_apros','companyinvoicingdetails'),(46,'admin_apros','dashboardadminquickfilter'),(51,'admin_apros','emailtemplate'),(48,'admin_apros','learnerdashboard'),(50,'admin_apros','learnerdashboarddiscovery'),(55,'admin_apros','learnerdashboardmilestone'),(56,'admin_apros','learnerdashboardmilestoneprogress'),(49,'admin_apros','learnerdashboardtile'),(52,'admin_apros','tilebookmark'),(38,'admin_apros','userregistrationbatch'),(37,'admin_apros','userregistrationerror'),(2,'auth','group'),(1,'auth','permission'),(3,'contenttypes','contenttype'),(18,'courses','featureflags'),(17,'courses','lessonnotesitem'),(19,'license','licensegrant'),(16,'main','curatedcontentitem'),(54,'mcka_apros_test','sessiontest'),(53,'mcka_apros_test','usertest'),(20,'public_api','apitoken'),(4,'sessions','session'),(5,'south','migrationhistory');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2016-07-11 09:36:47.039322'),(2,'auth','0001_initial','2016-07-11 09:36:47.073702'),(3,'accounts','0001_initial','2016-07-11 09:36:47.112177'),(4,'accounts','0002_auto_20160705_1123','2016-07-11 09:36:47.406547'),(5,'admin','0001_initial','2016-07-11 09:36:47.510661'),(6,'admin_apros','0001_initial','2016-07-11 09:36:47.616383'),(7,'contenttypes','0002_remove_content_type_name','2016-07-11 09:36:47.790896'),(8,'auth','0002_alter_permission_name_max_length','2016-07-11 09:36:47.852644'),(9,'auth','0003_alter_user_email_max_length','2016-07-11 09:36:47.884574'),(10,'auth','0004_alter_user_username_opts','2016-07-11 09:36:47.914651'),(11,'auth','0005_alter_user_last_login_null','2016-07-11 09:36:47.943797'),(12,'auth','0006_require_contenttypes_0002','2016-07-11 09:36:47.949422'),(13,'courses','0001_initial','2016-07-11 09:36:47.970196'),(14,'license','0001_initial','2016-07-11 09:36:47.987785'),(15,'main','0001_initial','2016-07-11 09:36:48.007020'),(16,'main','0002_auto_20160607_1249','2016-07-11 09:36:48.069317'),(17,'public_api','0001_initial','2016-07-11 09:36:48.085216'),(18,'sessions','0001_initial','2016-07-11 09:36:48.110110'),(19,'mcka_apros_test','0001_initial','2016-07-11 10:46:38.327608'),(21,'admin_apros','0002_learnerdashboardmilestone_learnerdashboardmilestoneprogress','2016-08-23 12:19:01.389096');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_b7b81f0c` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('045jx0li01q9lmx3gvgi5a9g79a7bdpz','NDhiOGIxM2NlMGQxMzkyMzZiODlmZmE4MTdhNGRhZWI4MTFkOWMwNjqAAn1xAShVFGxlYXJuZXJfZGFzaGJvYXJkX2lkcQKKAQFVE2NsaWVudF9kaXNwbGF5X25hbWVxA1gUAAAATWNLaW5zZXkgYW5kIENvbXBhbnlxBFUScmVtb3RlX3Nlc3Npb25fa2V5cQVYIAAAADQ2ZThjMjg1ZGMwNmQwNTEyZjk3NDdlYzViZTQ0MTdmcQZVDV9hdXRoX3VzZXJfaWRxB1gDAAAAMTkxcQhVCmxhc3RfdG91Y2hxCWNkYXRldGltZQpkYXRldGltZQpxClUKB+AHCww7Ago3hIVScQtVEl9hdXRoX3VzZXJfYmFja2VuZHEMVSFhY2NvdW50cy5qc29uX2JhY2tlbmQuSnNvbkJhY2tlbmRxDVUDZGR0cQ6JVQljb3Vyc2VfaWRxD1gfAAAAY291cnNlLXYxOmVkWCtEZW1vWCtEZW1vX0NvdXJzZXEQVQ9jdXJyZW50X3Byb2dyYW1xEWNhZG1pbi5tb2RlbHMKUHJvZ3JhbQpxEimBcRN9cRQoVQdjb3Vyc2VzcRVdcRZjYXBpX2NsaWVudC5jb3Vyc2VfbW9kZWxzCkNvdXJzZQpxFymBcRh9cRkoVQNlbmRxGk5VBG5hbWVxG1gYAAAAZWRYIERlbW9uc3RyYXRpb24gQ291cnNlVQxjb3Vyc2VfY2xhc3NxHFUHY3VycmVudFUJaXNfYWN0aXZlcR2IVQN1cmlxHlhSAAAAaHR0cDovL2xtcy5tY2thLmxvY2FsL2FwaS9zZXJ2ZXIvdXNlcnMvMTkxL2NvdXJzZXMvY291cnNlLXYxOmVkWCtEZW1vWCtEZW1vX0NvdXJzZVUFc3RhcnRxH2gKVQoH3QIFBQAAAAAAhVJxIFUQcGVyY2VudF9jb21wbGV0ZXEhSxlVAmlkcSJYHwAAAGNvdXJzZS12MTplZFgrRGVtb1grRGVtb19Db3Vyc2VVE19jYXRlZ29yaXNlZF9wYXJzZXJxI051YmFVD291dHNpZGVfY291cnNlc3EkTlUMZGlzcGxheV9uYW1lcSVVG01jS2luc2V5IE1hbmFnZW1lbnQgUHJvZ3JhbXEmaCJVCk5PX1BST0dSQU1xJ2gbaCZ1YlUSY3VycmVudF9wcm9ncmFtX2lkcShoJ1UPX2F1dGhfdXNlcl9oYXNocSlVKGEzOTVhYzFhMWI1NjJlNjRmOTMwMTU0MDBmYzYwMWVhMDU1MTFlODBxKnUu','2016-07-25 12:59:04'),('0a97sdfec87wcadfs6aqcia6pdvpgdg4','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-07 13:23:19'),('0dz85du3ggxcvtqiqrjqxhxmugumnq5n','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-26 13:06:08'),('0iu2imdjonksowg3e50v86me12xp8jmy','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-07 13:23:19'),('0kfzaso0s8r42lfq18a3pjtog0fcbmkx','NDExODgwMTVmZmIzZDE3NzUzNmFlMDg3Yzc4MTVhNmMwNTdhNjhhYTqAAn1xAShVEnJlbW90ZV9zZXNzaW9uX2tleVggAAAANzM5YmQ5Mjg1ZWU2YWFiYzdiZjJkZTliMzZmMmNmYzRVDV9hdXRoX3VzZXJfaWRYAQAAADVVCmxhc3RfdG91Y2hjZGF0ZXRpbWUKZGF0ZXRpbWUKcQJVCgfgCBcNGioM5h2FUnEDVRJfYXV0aF91c2VyX2JhY2tlbmRVIWFjY291bnRzLmpzb25fYmFja2VuZC5Kc29uQmFja2VuZFUDZGR0iVUPY3VycmVudF9wcm9ncmFtY2FkbWluLm1vZGVscwpQcm9ncmFtCnEEKYFxBX1xBihVDGRpc3BsYXlfbmFtZXEHWA0AAABOZXdfUHJvZ3JhbV8xcQhVBG5hbWVxCVgNAAAATmV3X1Byb2dyYW1fMVUIZW5kX2RhdGVxCmgCVQoH4gEBAAAAAAAAhVJxC1UEZGF0YXEMY2FwaV9jbGllbnQuanNvbl9vYmplY3QKT2JqZWN0aWZpZXIKcQ0pgXEOfXEPKGgHaAhVCnN0YXJ0X2RhdGVxEFgbAAAAMjAxNi0wMS0wMVQwMDowMDowMC4wMDAwMDBaaApYGwAAADIwMTgtMDEtMDFUMDA6MDA6MDAuMDAwMDAwWnViVQN1cmlxEVgqAAAAaHR0cDovL2xtcy5tY2thLmxvY2FsL2FwaS9zZXJ2ZXIvZ3JvdXBzLzEwVQJpZHESSwpVB2NvdXJzZXNxE11VD291dHNpZGVfY291cnNlc3EUXVUEdHlwZXEVWAYAAABzZXJpZXNoEGgCVQoH4AEBAAAAAAAAhVJxFlUJcmVzb3VyY2VzcRddcRgoaA0pgXEZfXEaaBFYMAAAAGh0dHA6Ly9sbXMubWNrYS5sb2NhbC9hcGkvc2VydmVyL2dyb3Vwcy8xMC91c2Vyc3NiaA0pgXEbfXEcaBFYMQAAAGh0dHA6Ly9sbXMubWNrYS5sb2NhbC9hcGkvc2VydmVyL2dyb3Vwcy8xMC9ncm91cHNzYmgNKYFxHX1xHmgRWDIAAABodHRwOi8vbG1zLm1ja2EubG9jYWwvYXBpL3NlcnZlci9ncm91cHMvMTAvY291cnNlc3NiZXViVRJjdXJyZW50X3Byb2dyYW1faWRLClUPX2F1dGhfdXNlcl9oYXNoVShhMzk1YWMxYTFiNTYyZTY0ZjkzMDE1NDAwZmM2MDFlYTA1NTExZTgwdS4=','2016-09-06 13:26:44'),('0kqkhblpqwz6x5qu3zqeq2lc9oy2qsmm','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 09:49:33'),('0l9cyuwjihlyekzx07ea7gz00zkusukl','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-12 11:42:55'),('0lm5n40n86isyam46apt4on950erslea','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-18 11:42:19'),('0qr0rmel0y95kauc99t5omj958xp03k6','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-18 11:42:19'),('0y8ymtdod54cec8ylk5qet650mbqqor3','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-15 11:26:03'),('18vvohu1tk15frcraa32fapcbvfrluu2','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-15 12:14:54'),('1c4cceqb2uguoalrehppltfwukfeqjwf','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-17 12:54:56'),('1k9iu490c0vhawxlsww4lmekj6gmm8ua','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-25 08:28:16'),('1ob2dqoq6s3usai4biw1qk2n9jhvssrr','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-06-07 09:52:33'),('1y6uofdvtyyz3xi3rzomv9gyaj1mn5yv','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-10 12:18:00'),('2502xvibula5hiz5okbm42gxirgfmwb2','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-08 12:07:41'),('2espzxy86f5u6jhxz829s3p85nbwyvlq','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-06-14 13:12:11'),('2uhu7e139nyeu368rp8azbeurpdedehd','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-18 10:59:48'),('2xtb2ecok0qqt44ak0pvxlqbng9okb87','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-15 10:52:20'),('34fx8ltvczpoon5cydix80cgh690rn1r','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-10 12:05:43'),('3bjzjtbvq5mxfk1pfvv3ace5amaop4s9','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-02 12:47:12'),('3ouba5kugvo6go5iliazc9b4lc7eckzl','MDYwMzVkMzc0ZDk0OTIzNDFlZmI3N2U5YzBkODhhZWRmNjY2ZjhhOTqAAn1xAShVEl9hdXRoX3VzZXJfYmFja2VuZHECVSFhY2NvdW50cy5qc29uX2JhY2tlbmQuSnNvbkJhY2tlbmRxA1UScmVtb3RlX3Nlc3Npb25fa2V5cQRYIAAAADc1NjI5NWQwZjkyZGYzZDA1NDczZmZjMWFlYWVhMGZkcQVVDV9hdXRoX3VzZXJfaWRxBku/VQNkZHRxB4l1Lg==','2016-05-10 12:18:05'),('3pp29td8px5w5lyctjvss4nudbshlv2t','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-26 08:26:45'),('3r0tc9bxkswiiktoqifeko9l2k71cciv','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 08:50:57'),('3rgp1zylei5nv4c9t6mqtozgtjur6flp','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-05 11:03:36'),('42qwchco195ndmyktzt61dm9q2hd04qt','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-26 10:29:36'),('4526kmivz42go8xh8h6gkegpwxa1kvw0','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 10:32:44'),('4almdkxugbdorzn5c0f5nwpgzmjd1roi','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-06-14 08:12:02'),('4pfvczt99j3lxz1erc5bm7kvsbb4fyj2','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-06-14 13:12:11'),('4unc16jfc1ibp05d5fvt67lmyf35ltu6','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-06 12:46:15'),('4x3is7y5jmbeqcj7on0iaeu5pwa2tvdd','Y2E0MDJiMjNmZTRlYzFkMjgyNzdiZGMyZTBhNTE0ZmMyMDczNzUzMDqAAn1xAShVEl9hdXRoX3VzZXJfYmFja2VuZHECVSFhY2NvdW50cy5qc29uX2JhY2tlbmQuSnNvbkJhY2tlbmRxA1UScmVtb3RlX3Nlc3Npb25fa2V5cQRYIAAAAGY4MGEzY2YzYWE2MmZjYWE1Njc1Y2NmM2JlNmI3MWUxcQVVDV9hdXRoX3VzZXJfaWRxBku/VQNkZHRxB4l1Lg==','2016-05-09 07:51:53'),('4ycmf36sn5g3z25hh3olw0dvfcl9p28b','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-15 09:33:59'),('50av0cmb484j8cbdi5wriz292labc16d','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-26 13:06:08'),('564iy8oqsxkpsqmxh2c5ueo9na3rt3a7','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-06-14 08:10:58'),('5d6rii5zrgh79l00yepvfn91xozs5qap','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-05 11:03:36'),('5i37nmrbp01wk7vwjdn9yj03crk8ikqs','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-26 12:32:44'),('5ivuoubl219sgcoa01vhmucgt71v7x6b','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-06-27 12:40:39'),('5lxgj1rth8hnp3andkpvm1zmnx4p32eh','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 15:09:15'),('5w2960jwohyd9p11rjz8xxr5x0mosv9t','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-06-14 13:12:48'),('5wa7bnadgxd2o8gz6zd4utcmo3ytbxzd','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-03 12:47:21'),('6dgtwxi5pn7v50i1b8tscn4qyjiz0987','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 09:49:33'),('6lc8xufg7zh2yuw35krkr0uknn4poyol','OTlhYjYzZjFkOWY0NTA2OTdlNDBjOWY0MGY3YmVhYjAwNDE0YWJmNDqAAn1xAShVEnJlbW90ZV9zZXNzaW9uX2tleXECWCAAAAA5YWI1MjY3ZTJhMmRkOTlkOTlkNzA0NTUxMzE1Y2YyZHEDVQ1fYXV0aF91c2VyX2lkcQRLv1UKbGFzdF90b3VjaHEFY2RhdGV0aW1lCmRhdGV0aW1lCnEGVQoH4AMRDjADBB2EhVJxB1USX2F1dGhfdXNlcl9iYWNrZW5kcQhVIWFjY291bnRzLmpzb25fYmFja2VuZC5Kc29uQmFja2VuZHEJVQNkZHRxColVD2N1cnJlbnRfcHJvZ3JhbXELY2FkbWluLm1vZGVscwpQcm9ncmFtCnEMKYFxDX1xDihVB2NvdXJzZXNxD11xEGNhcGlfY2xpZW50LmNvdXJzZV9tb2RlbHMKQ291cnNlCnERKYFxEn1xEyhVA2VuZHEUTlUEbmFtZXEVWBgAAABlZFggRGVtb25zdHJhdGlvbiBDb3Vyc2VVDGNvdXJzZV9jbGFzc3EWVQdjdXJyZW50cRdVCWlzX2FjdGl2ZXEYiFUDdXJpcRlYUgAAAGh0dHA6Ly9sbXMubWNrYS5sb2NhbC9hcGkvc2VydmVyL3VzZXJzLzE5MS9jb3Vyc2VzL2NvdXJzZS12MTplZFgrRGVtb1grRGVtb19Db3Vyc2VVBXN0YXJ0cRpoBlUKB90CBQUAAAAAAIVScRtVEHBlcmNlbnRfY29tcGxldGVxHEsZVQJpZHEdWB8AAABjb3Vyc2UtdjE6ZWRYK0RlbW9YK0RlbW9fQ291cnNlVRNfY2F0ZWdvcmlzZWRfcGFyc2VycR5OdWJhVQ9vdXRzaWRlX2NvdXJzZXNxH05VDGRpc3BsYXlfbmFtZXEgVRtNY0tpbnNleSBNYW5hZ2VtZW50IFByb2dyYW1xIWgdVQpOT19QUk9HUkFNcSJoFWghdWJVEmN1cnJlbnRfcHJvZ3JhbV9pZHEjaCJ1Lg==','2016-03-31 14:48:06'),('6ny3aggx5kqmfnoszcz4prxnkwzhy74x','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-06 09:45:04'),('7aflq13i57gjqd9jo084ydzazmsy7nd1','MGRkMTI0ODg1ZDkzNTU0ZWY0MTE0MDEyMzBjMjNiMDgzOGNlYTIxYzqAAn1xAShVEnJlbW90ZV9zZXNzaW9uX2tleXECWCAAAABhOWMwZTZlZDdiYmJhMTMxZTc2NjhmMTkxOTBlOTVjMnEDVQ1fYXV0aF91c2VyX2lkcQRLv1USX2F1dGhfdXNlcl9iYWNrZW5kcQVVIWFjY291bnRzLmpzb25fYmFja2VuZC5Kc29uQmFja2VuZHEGVQNkZHRxB4lVD2N1cnJlbnRfcHJvZ3JhbXEIY2FkbWluLm1vZGVscwpQcm9ncmFtCnEJKYFxCn1xCyhVB2NvdXJzZXNxDF1xDWNhcGlfY2xpZW50LmNvdXJzZV9tb2RlbHMKQ291cnNlCnEOKYFxD31xEChVA2VuZE5VBG5hbWVYGAAAAGVkWCBEZW1vbnN0cmF0aW9uIENvdXJzZVUJaXNfYWN0aXZliFUDdXJpWFIAAABodHRwOi8vbG1zLm1ja2EubG9jYWwvYXBpL3NlcnZlci91c2Vycy8xOTEvY291cnNlcy9jb3Vyc2UtdjE6ZWRYK0RlbW9YK0RlbW9fQ291cnNlVQVzdGFydGNkYXRldGltZQpkYXRldGltZQpxEVUKB90CBQUAAAAAAIVScRJVEHBlcmNlbnRfY29tcGxldGVxE0sZVQJpZFgfAAAAY291cnNlLXYxOmVkWCtEZW1vWCtEZW1vX0NvdXJzZVUTX2NhdGVnb3Jpc2VkX3BhcnNlcnEUTnViYVUPb3V0c2lkZV9jb3Vyc2VzcRVOVQxkaXNwbGF5X25hbWVxFlUbTWNLaW5zZXkgTWFuYWdlbWVudCBQcm9ncmFtcRdVAmlkcRhVCk5PX1BST0dSQU1xGVUEbmFtZXEaaBd1YlUSY3VycmVudF9wcm9ncmFtX2lkcRtoGXUu','2016-04-08 08:57:58'),('7b0s7ha34yqej3mwmx7w8ftwz9o6140q','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-18 12:35:48'),('7bslofmsb9mccl7fu2yitp1euzivbcvy','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-18 10:39:17'),('7rws9yydpc2draypkmzpwnjhvup4sxkm','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-29 11:38:38'),('7vmtopgz6y6nmk7m8zltbapxnahl3w0n','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-28 13:56:10'),('8ewcl80fynx7vw5cjeeo3cazxxw7zvm8','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-08 13:46:00'),('8zb5szca1g95niczxbzpdcq3mnhlmpyw','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-21 08:24:01'),('93wzx3ksgmolvk0bfczqe66jczeav71q','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-18 12:35:48'),('9cnzlpafq7jozcia7k8gtfrmnmo36qx8','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-06 11:27:07'),('9f13cbcqw659nrx6rflqcj0b0azrj92p','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-18 10:59:48'),('9jt198y4evuuxizrzood5a6loeknsvyc','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-09 08:18:17'),('ae1gbnb51wexchtb15tervmzc22u7l89','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-05 10:47:10'),('af4jgd0tthiu8zzughdq175ecfd85p03','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-08 10:37:49'),('bth1ga1qo8ljes1tdajnnf6b906f5nyx','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-10 12:05:44'),('c8b7hcar3rne5d8by51qtao10vwwd8k6','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-06 12:46:15'),('cgr6lcf0awmbkn36mv98px6qm4ttkqk5','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-26 12:32:44'),('cgzz6hvm23ybsqex5phpdyrhd0bz1u0h','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 11:11:13'),('chan5gh8z4bezm2fwymvaxaqb3wz8a3p','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-06-14 13:12:48'),('ciij61su6e557kqkp5obvg0fksqf75vj','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 08:44:41'),('d16vfc1pkyoqjlrze7igf7hn9va94s8j','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-20 11:08:35'),('ditjnixev8vm2xx5wf4pplam493161k2','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-15 08:26:12'),('dq4i1o3zot90unnhok21hwi56fs2hm0o','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 11:11:13'),('e6azd9uog0hi99zxrfsvzyg3drrptnlx','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-03 13:06:01'),('e7kvdluui62e7c3m40y5neelfvw9f9v6','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-20 11:08:35'),('ebvtsoudgox5igaua4up0o2p8431vc9r','OGJiOTEwZjc5NzM4NDIzOTk4Mzc3OGMxZDI2NWU4ZTQ5ODk4OWUxYTqAAn1xAShVEWN1cnJlbnRfY291cnNlX2lkTlUScmVtb3RlX3Nlc3Npb25fa2V5WCAAAAAwNDhkMjhhMjQyZjMyZjgzODFlMGE1NWU4MWU5ZWYzN1UNX2F1dGhfdXNlcl9pZEsFVQpsYXN0X3RvdWNoY2RhdGV0aW1lCmRhdGV0aW1lCnECVQoH4AMQDjcvDqllhVJxA1USX2F1dGhfdXNlcl9iYWNrZW5kVSFhY2NvdW50cy5qc29uX2JhY2tlbmQuSnNvbkJhY2tlbmRVA2RkdIlVD2N1cnJlbnRfcHJvZ3JhbWNhZG1pbi5tb2RlbHMKUHJvZ3JhbQpxBCmBcQV9cQYoVQxkaXNwbGF5X25hbWVxB1gNAAAATmV3X1Byb2dyYW1fMXEIVQRuYW1lcQlYDQAAAE5ld19Qcm9ncmFtXzFVCGVuZF9kYXRlcQpoAlUKB+IBAQAAAAAAAIVScQtVBGRhdGFxDGNhcGlfY2xpZW50Lmpzb25fb2JqZWN0Ck9iamVjdGlmaWVyCnENKYFxDn1xDyhoB2gIVQpzdGFydF9kYXRlcRBYGwAAADIwMTYtMDEtMDFUMDA6MDA6MDAuMDAwMDAwWmgKWBsAAAAyMDE4LTAxLTAxVDAwOjAwOjAwLjAwMDAwMFp1YlUDdXJpcRFYKgAAAGh0dHA6Ly9sbXMubWNrYS5sb2NhbC9hcGkvc2VydmVyL2dyb3Vwcy8xMFUCaWRxEksKVQdjb3Vyc2VzcRNdVQ9vdXRzaWRlX2NvdXJzZXNxFF1VBHR5cGVxFVgGAAAAc2VyaWVzaBBoAlUKB+ABAQAAAAAAAIVScRZVCXJlc291cmNlc3EXXXEYKGgNKYFxGX1xGmgRWDAAAABodHRwOi8vbG1zLm1ja2EubG9jYWwvYXBpL3NlcnZlci9ncm91cHMvMTAvdXNlcnNzYmgNKYFxG31xHGgRWDEAAABodHRwOi8vbG1zLm1ja2EubG9jYWwvYXBpL3NlcnZlci9ncm91cHMvMTAvZ3JvdXBzc2JoDSmBcR19cR5oEVgyAAAAaHR0cDovL2xtcy5tY2thLmxvY2FsL2FwaS9zZXJ2ZXIvZ3JvdXBzLzEwL2NvdXJzZXNzYmV1YlUSY3VycmVudF9wcm9ncmFtX2lkSwp1Lg==','2016-03-30 14:55:48'),('eofvy9e3cp0if4687q97srlnaz5ay1h5','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 15:38:58'),('eulamduowa64t90marfjuw9nd41xi58e','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-06-03 09:29:20'),('f1xvg54fmp8x6uxrmehzts9a7fiuvcul','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-29 08:55:50'),('f72wgnlbged84lbdbx52nw7z1306zro5','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-05 10:56:05'),('foefcmrvl3u9332qviqxmlnufm00n0z1','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-03 14:35:21'),('fq964pwm3ilx1isg9d9xba4sqrsxfwma','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 09:49:33'),('fsildpkneuza0c4ry8rwq2ncg4eckffe','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-19 11:29:10'),('fzzf1wn9cnuhnuv7naeq4htco6i3rzuo','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-18 11:21:59'),('g2qxkeac174wipyz4bpwi6n2nga0mas4','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-18 10:59:48'),('g5ns2tiraeu6km3eesruskk5tb7roi4i','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-13 13:47:22'),('g5vjgugg3w1jcky3b1jqggk0efs1xwe3','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-03 14:35:21'),('ga91bvsqfgk68kimcoc0cn4pr6tjf6f0','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-06 12:46:15'),('gg3y69o4a2qjjocm496f7x7o6pq46zp9','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-10 09:19:50'),('h5h58wxpghoxnjblsb4wh0j7rp4nkja6','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 08:56:45'),('hlelr4p6qs4o45s1qvwifa2ggenlvegp','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-20 10:25:51'),('i2qjn9eul32ddths4lhz9cn7gv0e4cgs','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-12 12:19:46'),('i58waidna8cq9t19j86aws6r7djnc380','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-07-14 08:59:25'),('i97a7nk5rjkw51pawal9fd3uf3pjtzav','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-26 12:47:29'),('ifj5omnvsgnsank4sywbd8hierhri4bi','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-18 10:59:48'),('j5nvw0gb9mqjxiyjt9osq32pdq26jx83','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-18 10:18:12'),('j6hyi26clrydvxjcobmch01p5nklxwt6','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-09 08:18:17'),('jf7qjrdiatr9hgonxhcyiw8ea3wvrf20','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-04 08:45:18'),('jhx5zxp2w8ftge34iw4w66euqoyfaz40','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-26 10:29:36'),('jmx1ywyrqn260r2eghkepbytkb270vbu','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-15 10:52:20'),('jps4lfy31co37t0tftvbdwlek1x8710y','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-04 08:29:43'),('jtp4tsnt3jw6acm6affkcw0zbovhh56t','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-20 10:25:51'),('k5q2w8c7f9f0kf5f2ybuomduxyuswpfl','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-13 13:47:21'),('kebegg8krdpz2shqpd3v18g3w5wrc3s7','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-05 10:56:05'),('knc758lcgi7crm8u8cyyaueyie6qysbb','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-06-14 12:46:39'),('kuml609729ctlcm74kb63iowtk3bo4yn','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-07-14 08:59:25'),('l3403k7g2fd7jlqbfb6gjq7u16hu05iu','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-03 12:47:21'),('l90vqphqn3xyyjs282puur7no9ul1voa','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-25 11:33:24'),('lfl06q47bgx3p52c4dvtj2zg5fnb1ko3','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-18 12:35:49'),('lnidjm9bvkaatwu43vqfbmegvxjr2zqb','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-18 11:21:59'),('lwlddf59am0yk13059kah9zdsgkjygzj','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 08:56:45'),('m6um9trap6cy4vys8147slf3yfvrv6y8','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-29 09:04:22'),('mdj9u1jvwnzm6gmp1i646wczmdbs9m1o','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 10:46:09'),('mij8w9u86ugqnx5c2ezvnh9fszko41ej','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-29 10:17:40'),('mtrolexv0sojty2rh7j9w3hf16hnx8gz','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-18 10:59:48'),('mv40o5hmy6at8z79eus0drn3o4du96ep','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-29 10:17:40'),('mvk10znx68h1hzf0nzqqid4zz0z6vhem','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-10 09:19:50'),('nej6eautya0mdps4gicz64zsfpscktpo','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-09 09:01:57'),('ngztqwmlalz2s861x92akyg5dcfdi830','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-05 11:25:00'),('nrigmmebmqfperq82zuyxt786rrwtmkx','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 15:09:15'),('nua5ga5l7xyufoaa7w0abv2wqw2wp08o','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 08:50:57'),('o0f59vugz29tzq3b9rceuf9y9se907fb','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-04 08:45:18'),('o21ecvb5h9puevau9zieoav7r2hbwqik','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-07-14 08:59:25'),('o7fjn6ilhupxnvs6xvgc7ayk9de5o33q','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-12 12:19:46'),('o8isumhumnpunifu0ndf58e02386wo2m','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-19 12:42:52'),('o8tdfitmvobnp4eptxf79a6qay4fgzub','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 15:38:58'),('octvsvqlzq26f1bdsjpfmyh1dxginpwf','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-05 11:25:00'),('or8a3bhtuaxk2f9zojr6ys9mnwf8xypu','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-29 11:02:46'),('p553en8bxdwzmqlhf22xz0r5kdkgaie4','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-25 11:33:24'),('p7z402111zjcvdp76rpxwxmzbr7qiejz','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-04 15:00:14'),('po33xk7ljssv72ty5sf8bnr51xk8odvn','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-26 10:29:36'),('pwzxd3z41zoz6w8sjoktizwqge43tiyw','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-20 11:40:12'),('pzurzsf75jamf0fvvtshrp89pg2imic0','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-07 13:23:19'),('q5xxgmjiar0wgmgj5qsyts7x55dbdqbe','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-07 12:40:31'),('qbdhjyhxyakwr5gxpoj3db4o3z4t9u0d','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-08 13:46:00'),('qkcb3jyhxsk4iz4p2um2aonrr8pjrpmk','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-01 10:59:20'),('qmo8vu8hk2m9rzflmt2ecitlq4vosib7','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-15 08:26:12'),('qnpm2vox40rdz9o1n1ndwuh9klz2r8ae','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 08:44:41'),('r7s7t0v3mqdwjufujg337tofuhi6gvia','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-21 08:13:03'),('rapboebiiu6amub54du4fbv0e5d46ajr','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-29 09:04:22'),('rj6ifnx0kq4bwdhe6wi0sbtklpdkf7r4','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-25 11:09:30'),('rl5acpexsfcwrd5m82wzdh83pzyqei9e','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-15 12:28:03'),('rncto6a0nm7xmtesujilucjffushvk9v','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-06 12:08:36'),('rob5tht04rthe2zzcx35pnbsjtstyhuj','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-07-14 10:08:54'),('s1ce2xchs7o8egkhvmhj0xolhdeje1r0','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-04 15:00:14'),('saxw81ydk7c6oj6n0kfzut5g7mehktmw','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-04 07:30:05'),('sbxmag5eurq7p9kvm61kv6lire4ongrw','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-15 09:34:00'),('skpr9i7gsyccwfrhnestg7kbr4otsquj','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 15:15:27'),('sm29hm4lnkprqn557bxhuiy799netpic','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 12:02:03'),('sqm733pxu3gsriaqkypqqrijgxzg4hf4','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-27 14:06:29'),('srd0fhjmfdqy1xr9nzl61i4o0dv0sh32','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-06-14 12:09:31'),('sy3fs5oezu5ozhs03is99rh4alna3mg1','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-26 12:32:44'),('szwjer629y6ls0khy5drb9t0shk0jirr','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-09 08:07:18'),('t4hk7xwuroire7tutzdhed7tpsl43w9v','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-07-14 08:59:25'),('t6pfmvi0n891kdee8dbr633k77vebu2u','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-18 11:21:59'),('u2j5wax6idz2ok9keo5gmvbthbhnvg45','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-06 09:45:04'),('u9663g5nsv8ex7jcviva5auup8dp0ckm','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-03 13:27:03'),('ubkzbqq65pf189b13w27psngnxdxdtl3','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-07 12:40:31'),('udp8r4zpx0bfy2rrmk4yearwk9qs0g4b','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-25 08:28:15'),('udpkastnk3u4i7kbrn72g7curfugcdqq','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-25 11:33:24'),('uijw4z9t7asxnmsdtfjn6c4q6c5t1se1','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-06 09:45:05'),('uoepr44hq81nsjzzo7558265nrxxouk1','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-15 11:36:54'),('uqi3tj4y5p7ge3hh54xdz2q0inx9nw1g','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 08:56:45'),('uyx3xntayigqngsolztfrmggy6ex1v5i','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-07-14 10:08:54'),('v3aisf5tl2grh4gggok9y48fheq3imsh','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-06-14 12:10:13'),('v6l8c2m9clf5ie7p6btaz5iw7z394rej','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 08:50:57'),('vgyhylaw9tj3rdlcsfz2144h3a3h7iyj','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 10:32:44'),('vprwtakh5soep9b7z70rfdd8j58m7j1a','MWMzM2ZmYjYwNGNlZmQyNzhiMDUxNmY3MWIxZjQ1NjZmMzEyNDNjNTqAAn1xAShVEl9hdXRoX3VzZXJfYmFja2VuZHECVSFhY2NvdW50cy5qc29uX2JhY2tlbmQuSnNvbkJhY2tlbmRxA1UScmVtb3RlX3Nlc3Npb25fa2V5cQRYIAAAADQ5NjRmMjEwOGYzMTg4MmQ2MWY0ZmNmNTBlZWVhZTgzcQVVDV9hdXRoX3VzZXJfaWRxBkvdVQNkZHRxB4l1Lg==','2016-05-09 09:02:05'),('vtea3ag24i3d28egb77fhvav1qegiy8f','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-07-14 08:59:25'),('vvlsy3nmdezmhe7uzaa8r1s1hpxyvxd9','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-13 13:47:21'),('vzk67au1c8n9qdikbj28ip8d8itn9l37','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-04 07:30:05'),('w2y16oipbtht2kc49cri13dp1xqku6mm','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-15 13:47:36'),('wekb3g1spr7c2ouv1kgxj1d4v90qle7t','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 10:46:09'),('wkf9eujyp1j6urdccdwakkzr4skx5zkt','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-25 08:28:16'),('wnbg3ko7znmei4iyibcp43dbghnmw8ks','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-29 10:17:40'),('wskm0m033v5a998ci0q0svg5lojz9egb','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-07-15 08:32:54'),('wuw8zj4r1j9c76ty56ufhdmbbgfyzafd','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-07-14 08:59:25'),('ww2qvnd0pmdcc4mtxd806foo0qkbypn5','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-10 12:18:00'),('wwpzgr9x5mknrjht03kal3fb47zarhn7','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-03 12:47:21'),('xfx865bnpmr6aio2ymgptg13eokvzm3l','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-12 12:19:46'),('xq4ob1ehf4r0jwe9k1j3bcwqj4c06s6d','NzU3NjI5ZGFjYzM4MWY0YmFjZmI4MDM0MzQxOTU3YWQyNDRmNWM3MTqAAn1xAShVEWN1cnJlbnRfY291cnNlX2lkcQJYHwAAAGNvdXJzZS12MTplZFgrRGVtb1grRGVtb19Db3Vyc2VxA1UScmVtb3RlX3Nlc3Npb25fa2V5cQRYIAAAADUxMzMxYjIyNmI5NzIzZWU5ZGUxYTFkZGRmZTkyMGNlcQVVDV9hdXRoX3VzZXJfaWRxBku/VQpsYXN0X3RvdWNocQdjZGF0ZXRpbWUKZGF0ZXRpbWUKcQhVCgfgAxkIOhEAydKFUnEJVRJfYXV0aF91c2VyX2JhY2tlbmRxClUhYWNjb3VudHMuanNvbl9iYWNrZW5kLkpzb25CYWNrZW5kcQtVA2RkdHEMiVUPY3VycmVudF9wcm9ncmFtcQ1jYWRtaW4ubW9kZWxzClByb2dyYW0KcQ4pgXEPfXEQKFUHY291cnNlc3ERXXESY2FwaV9jbGllbnQuY291cnNlX21vZGVscwpDb3Vyc2UKcRMpgXEUfXEVKFUDZW5kcRZOVQRuYW1lcRdYGAAAAGVkWCBEZW1vbnN0cmF0aW9uIENvdXJzZVUMY291cnNlX2NsYXNzcRhVB2N1cnJlbnRxGVUJaXNfYWN0aXZlcRqIVQN1cmlxG1hSAAAAaHR0cDovL2xtcy5tY2thLmxvY2FsL2FwaS9zZXJ2ZXIvdXNlcnMvMTkxL2NvdXJzZXMvY291cnNlLXYxOmVkWCtEZW1vWCtEZW1vX0NvdXJzZVUFc3RhcnRxHGgIVQoH3QIFBQAAAAAAhVJxHVUQcGVyY2VudF9jb21wbGV0ZXEeSxlVAmlkcR9YHwAAAGNvdXJzZS12MTplZFgrRGVtb1grRGVtb19Db3Vyc2VVE19jYXRlZ29yaXNlZF9wYXJzZXJxIE51YmFVD291dHNpZGVfY291cnNlc3EhTlUMZGlzcGxheV9uYW1lcSJVG01jS2luc2V5IE1hbmFnZW1lbnQgUHJvZ3JhbXEjaB9VCk5PX1BST0dSQU1xJGgXaCN1YlUSY3VycmVudF9wcm9ncmFtX2lkcSVoJHUu','2016-04-08 08:58:25'),('xy27nqc876yma8zecaan0g5gxntb6shw','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-15 09:33:59'),('yleygaxn3b6kokvgj40f10kb63czgtiv','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-14 15:15:27'),('yujqmsx5d1xuq1r17lqizti8ihh9e3kh','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-09 08:18:17'),('yvex05pzgcu3uy93ud7n50fq51yih502','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-20 11:40:12'),('yz2vxmdjgf8fze3acw5cd1rpckmf7w5e','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-18 10:18:12'),('zcnbcoxysur2xzycf37oejts8lnbf9ee','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-05 11:59:04'),('zm29qeeutl3ighj66ku7op0aub74b5h5','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-04 08:29:43'),('zpr8cbmxucrq124fkj3nkdzldb0do5my','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-05-04 08:29:43'),('zth2qi81gzu26t7mz9m1dgljxszawxer','YjVmYmY5ODlhMjQ3MmM5ZjM4MTZmYWM4ZGU2MWYyMDU0ZTVjZTViNTqAAn1xAShVEnJlbW90ZV9zZXNzaW9uX2tleXECWCAAAABmNTdhOTE5MTAxZThiYzgzZTBjZDMwNzQyN2I5YjE1ZnEDVQ1fYXV0aF91c2VyX2lkcQRLv1UKbGFzdF90b3VjaHEFY2RhdGV0aW1lCmRhdGV0aW1lCnEGVQoH4AMSDjovA0K+hVJxB1USX2F1dGhfdXNlcl9iYWNrZW5kcQhVIWFjY291bnRzLmpzb25fYmFja2VuZC5Kc29uQmFja2VuZHEJVQNkZHRxColVD2N1cnJlbnRfcHJvZ3JhbXELY2FkbWluLm1vZGVscwpQcm9ncmFtCnEMKYFxDX1xDihVB2NvdXJzZXNxD11xEGNhcGlfY2xpZW50LmNvdXJzZV9tb2RlbHMKQ291cnNlCnERKYFxEn1xEyhVA2VuZE5VBG5hbWVYGAAAAGVkWCBEZW1vbnN0cmF0aW9uIENvdXJzZVUMY291cnNlX2NsYXNzcRRVB2N1cnJlbnRxFVUJaXNfYWN0aXZliFUDdXJpWFIAAABodHRwOi8vbG1zLm1ja2EubG9jYWwvYXBpL3NlcnZlci91c2Vycy8xOTEvY291cnNlcy9jb3Vyc2UtdjE6ZWRYK0RlbW9YK0RlbW9fQ291cnNlVQVzdGFydGgGVQoH3QIFBQAAAAAAhVJxFlUQcGVyY2VudF9jb21wbGV0ZXEXSxlVAmlkWB8AAABjb3Vyc2UtdjE6ZWRYK0RlbW9YK0RlbW9fQ291cnNlVRNfY2F0ZWdvcmlzZWRfcGFyc2VycRhOdWJhVQ9vdXRzaWRlX2NvdXJzZXNxGU5VDGRpc3BsYXlfbmFtZXEaVRtNY0tpbnNleSBNYW5hZ2VtZW50IFByb2dyYW1xG1UCaWRxHFUKTk9fUFJPR1JBTXEdVQRuYW1lcR5oG3ViVRJjdXJyZW50X3Byb2dyYW1faWRxH2gddS4=','2016-04-01 14:58:50'),('zwmj5u1kvx17ycx0mefk3po6vy81yvzv','YjM4NTljZDE1MDE2MjFmZjYxNTVlNmM1YjM4ZDAyNGY1YzlmOTNmMzqAAn1xAS4=','2016-04-05 11:59:04');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `license_licensegrant`
--

DROP TABLE IF EXISTS `license_licensegrant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `license_licensegrant` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `license_uuid` varchar(36) NOT NULL,
  `granted_id` int(11) NOT NULL,
  `grantor_id` int(11) NOT NULL,
  `grantee_id` int(11) DEFAULT NULL,
  `granted_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3567 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `license_licensegrant`
--

LOCK TABLES `license_licensegrant` WRITE;
/*!40000 ALTER TABLE `license_licensegrant` DISABLE KEYS */;
INSERT INTO `license_licensegrant` VALUES (1,'',10,2,NULL,NULL),(2,'',10,2,NULL,NULL),(3,'',10,2,NULL,NULL),(4,'',10,2,NULL,NULL),(5,'',10,2,NULL,NULL),(6,'',10,2,NULL,NULL),(7,'',10,2,NULL,NULL),(8,'',10,2,NULL,NULL),(9,'',10,2,NULL,NULL),(10,'',10,2,NULL,NULL),(11,'',10,2,NULL,NULL),(12,'',10,2,NULL,NULL),(13,'',10,2,NULL,NULL),(14,'',10,2,NULL,NULL),(15,'',10,2,NULL,NULL),(16,'',10,2,NULL,NULL),(17,'',10,2,NULL,NULL),(18,'',10,2,NULL,NULL),(19,'',10,2,NULL,NULL),(20,'',10,2,NULL,NULL),(21,'',10,2,NULL,NULL),(22,'',10,2,NULL,NULL),(23,'',10,2,NULL,NULL),(24,'',10,2,NULL,NULL),(25,'',10,2,NULL,NULL),(26,'',10,2,NULL,NULL),(27,'',10,2,NULL,NULL),(28,'',10,2,NULL,NULL),(29,'',10,2,NULL,NULL),(30,'',10,2,NULL,NULL),(31,'',10,2,NULL,NULL),(32,'',10,2,NULL,NULL),(33,'',10,2,NULL,NULL),(34,'',10,2,NULL,NULL),(35,'',10,2,NULL,NULL),(36,'',10,2,NULL,NULL),(37,'',10,2,NULL,NULL),(38,'',10,2,NULL,NULL),(39,'',10,2,NULL,NULL),(40,'',10,2,NULL,NULL),(41,'',10,2,NULL,NULL),(42,'',10,2,NULL,NULL),(43,'',10,2,NULL,NULL),(44,'',10,2,NULL,NULL),(45,'',10,2,NULL,NULL),(46,'',10,2,NULL,NULL),(47,'',10,2,NULL,NULL),(48,'',10,2,NULL,NULL),(49,'',10,2,NULL,NULL),(50,'',10,2,NULL,NULL),(51,'',10,2,NULL,NULL),(52,'',10,2,NULL,NULL),(53,'',10,2,NULL,NULL),(54,'',10,2,NULL,NULL),(55,'',10,2,NULL,NULL),(56,'',10,2,NULL,NULL),(57,'',10,2,NULL,NULL),(58,'',10,2,NULL,NULL),(59,'',10,2,NULL,NULL),(60,'',10,2,NULL,NULL),(61,'',10,2,NULL,NULL),(62,'',10,2,NULL,NULL),(63,'',10,2,NULL,NULL),(64,'',10,2,NULL,NULL),(65,'',10,2,NULL,NULL),(66,'',10,2,NULL,NULL),(67,'',10,2,NULL,NULL),(68,'',10,2,NULL,NULL),(69,'',10,2,NULL,NULL),(70,'',10,2,NULL,NULL),(71,'',10,2,NULL,NULL),(72,'',10,2,NULL,NULL),(73,'',10,2,NULL,NULL),(74,'',10,2,NULL,NULL),(75,'',10,2,NULL,NULL),(76,'',10,2,NULL,NULL),(77,'',10,2,NULL,NULL),(78,'',10,2,NULL,NULL),(79,'',10,2,NULL,NULL),(80,'',10,2,NULL,NULL),(81,'',10,2,NULL,NULL),(82,'',10,2,NULL,NULL),(83,'',10,2,NULL,NULL),(84,'',10,2,NULL,NULL),(85,'',10,2,NULL,NULL),(86,'',10,2,NULL,NULL),(87,'',10,2,NULL,NULL),(88,'',10,2,NULL,NULL),(89,'',10,2,NULL,NULL),(90,'',10,2,NULL,NULL),(91,'',10,2,NULL,NULL),(92,'',10,2,NULL,NULL),(93,'',10,2,NULL,NULL),(94,'',10,2,NULL,NULL),(95,'',10,2,NULL,NULL),(96,'',10,2,NULL,NULL),(97,'',10,2,NULL,NULL),(98,'',10,2,NULL,NULL),(99,'',10,2,NULL,NULL),(100,'',10,2,NULL,NULL),(101,'',10,2,NULL,NULL),(102,'',10,2,NULL,NULL),(103,'',10,2,NULL,NULL),(104,'',10,2,NULL,NULL),(105,'',10,2,NULL,NULL),(106,'',10,2,NULL,NULL),(107,'',10,2,NULL,NULL),(108,'',10,2,NULL,NULL),(109,'',10,2,NULL,NULL),(110,'',10,2,NULL,NULL),(111,'',10,2,NULL,NULL),(112,'',10,2,NULL,NULL),(113,'',10,2,NULL,NULL),(114,'',10,2,NULL,NULL),(115,'',10,2,NULL,NULL),(116,'',10,2,NULL,NULL),(117,'',10,2,NULL,NULL),(118,'',10,2,NULL,NULL),(119,'',10,2,NULL,NULL),(120,'',10,2,NULL,NULL),(121,'',10,2,NULL,NULL),(122,'',10,2,NULL,NULL),(123,'',10,2,NULL,NULL),(124,'',10,2,NULL,NULL),(125,'',10,2,NULL,NULL),(126,'',10,2,NULL,NULL),(127,'',10,2,NULL,NULL),(128,'',10,2,NULL,NULL),(129,'',10,2,NULL,NULL),(130,'',10,2,NULL,NULL),(131,'',10,2,NULL,NULL),(132,'',10,2,NULL,NULL),(133,'',10,2,NULL,NULL),(134,'',10,2,NULL,NULL),(135,'',10,2,NULL,NULL),(136,'',10,2,NULL,NULL),(137,'',10,2,NULL,NULL),(138,'',10,2,NULL,NULL),(139,'',10,2,NULL,NULL),(140,'',10,2,NULL,NULL),(141,'',10,2,NULL,NULL),(142,'',10,2,NULL,NULL),(143,'',10,2,NULL,NULL),(144,'',10,2,NULL,NULL),(145,'',10,2,NULL,NULL),(146,'',10,2,NULL,NULL),(147,'',10,2,NULL,NULL),(148,'',10,2,NULL,NULL),(149,'',10,2,NULL,NULL),(150,'',10,2,NULL,NULL),(151,'',10,2,NULL,NULL),(152,'',10,2,NULL,NULL),(153,'',10,2,NULL,NULL),(154,'',10,2,NULL,NULL),(155,'',10,2,NULL,NULL),(156,'',10,2,NULL,NULL),(157,'',10,2,NULL,NULL),(158,'',10,2,NULL,NULL),(159,'',10,2,NULL,NULL),(160,'',10,2,NULL,NULL),(161,'',10,2,NULL,NULL),(162,'',10,2,NULL,NULL),(163,'',10,2,NULL,NULL),(164,'',10,2,NULL,NULL),(165,'',10,2,NULL,NULL),(166,'',10,2,NULL,NULL),(167,'',10,2,NULL,NULL),(168,'',10,2,NULL,NULL),(169,'',10,2,NULL,NULL),(170,'',10,2,NULL,NULL),(171,'',10,2,NULL,NULL),(172,'',10,2,NULL,NULL),(173,'',10,2,NULL,NULL),(174,'',10,2,NULL,NULL),(175,'',10,2,NULL,NULL),(176,'',10,2,NULL,NULL),(177,'',10,2,NULL,NULL),(178,'',10,2,NULL,NULL),(179,'',10,2,NULL,NULL),(180,'',10,2,NULL,NULL),(181,'',10,2,NULL,NULL),(182,'',10,2,NULL,NULL),(183,'',10,2,NULL,NULL),(184,'',10,2,NULL,NULL),(185,'',10,2,NULL,NULL),(186,'',10,2,NULL,NULL),(187,'',10,2,NULL,NULL),(188,'',10,2,NULL,NULL),(189,'',10,2,NULL,NULL),(190,'',10,2,NULL,NULL),(191,'',10,2,NULL,NULL),(192,'',10,2,NULL,NULL),(193,'',10,2,NULL,NULL),(194,'',10,2,NULL,NULL),(195,'',10,2,NULL,NULL),(196,'',10,2,NULL,NULL),(197,'',10,2,NULL,NULL),(198,'',10,2,NULL,NULL),(199,'',10,2,NULL,NULL),(200,'',10,2,NULL,NULL),(201,'',10,2,NULL,NULL),(202,'',10,2,NULL,NULL),(203,'',10,2,NULL,NULL),(204,'',10,2,NULL,NULL),(205,'',10,2,NULL,NULL),(206,'',10,2,NULL,NULL),(207,'',10,2,NULL,NULL),(208,'',10,2,NULL,NULL),(209,'',10,2,NULL,NULL),(210,'',10,2,NULL,NULL),(211,'',10,2,NULL,NULL),(212,'',10,2,NULL,NULL),(213,'',10,2,NULL,NULL),(214,'',10,2,NULL,NULL),(215,'',10,2,NULL,NULL),(216,'',10,2,NULL,NULL),(217,'',10,2,NULL,NULL),(218,'',10,2,NULL,NULL),(219,'',10,2,NULL,NULL),(220,'',10,2,NULL,NULL),(221,'',10,2,NULL,NULL),(222,'',10,2,NULL,NULL),(223,'',10,2,NULL,NULL),(224,'',10,2,NULL,NULL),(225,'',10,2,NULL,NULL),(226,'',10,2,NULL,NULL),(227,'',10,2,NULL,NULL),(228,'',10,2,NULL,NULL),(229,'',10,2,NULL,NULL),(230,'',10,2,NULL,NULL),(231,'',10,2,NULL,NULL),(232,'',10,2,NULL,NULL),(233,'',10,2,NULL,NULL),(234,'',10,2,NULL,NULL),(235,'',10,2,NULL,NULL),(236,'',10,2,NULL,NULL),(237,'',10,2,NULL,NULL),(238,'',10,2,NULL,NULL),(239,'',10,2,NULL,NULL),(240,'',10,2,NULL,NULL),(241,'',10,2,NULL,NULL),(242,'',10,2,NULL,NULL),(243,'',10,2,NULL,NULL),(244,'',10,2,NULL,NULL),(245,'',10,2,NULL,NULL),(246,'',10,2,NULL,NULL),(247,'',10,2,NULL,NULL),(248,'',10,2,NULL,NULL),(249,'',10,2,NULL,NULL),(250,'',10,2,NULL,NULL),(251,'',10,2,NULL,NULL),(252,'',10,2,NULL,NULL),(253,'',10,2,NULL,NULL),(254,'',10,2,NULL,NULL),(255,'',10,2,NULL,NULL),(256,'',10,2,NULL,NULL),(257,'',10,2,NULL,NULL),(258,'',10,2,NULL,NULL),(259,'',10,2,NULL,NULL),(260,'',10,2,NULL,NULL),(261,'',10,2,NULL,NULL),(262,'',10,2,NULL,NULL),(263,'',10,2,NULL,NULL),(264,'',10,2,NULL,NULL),(265,'',10,2,NULL,NULL),(266,'',10,2,NULL,NULL),(267,'',10,2,NULL,NULL),(268,'',10,2,NULL,NULL),(269,'',10,2,NULL,NULL),(270,'',10,2,NULL,NULL),(271,'',10,2,NULL,NULL),(272,'',10,2,NULL,NULL),(273,'',10,2,NULL,NULL),(274,'',10,2,NULL,NULL),(275,'',10,2,NULL,NULL),(276,'',10,2,NULL,NULL),(277,'',10,2,NULL,NULL),(278,'',10,2,NULL,NULL),(279,'',10,2,NULL,NULL),(280,'',10,2,NULL,NULL),(281,'',10,2,NULL,NULL),(282,'',10,2,NULL,NULL),(283,'',10,2,NULL,NULL),(284,'',10,2,NULL,NULL),(285,'',10,2,NULL,NULL),(286,'',10,2,NULL,NULL),(287,'',10,2,NULL,NULL),(288,'',10,2,NULL,NULL),(289,'',10,2,NULL,NULL),(290,'',10,2,NULL,NULL),(291,'',10,2,NULL,NULL),(292,'',10,2,NULL,NULL),(293,'',10,2,NULL,NULL),(294,'',10,2,NULL,NULL),(295,'',10,2,NULL,NULL),(296,'',10,2,NULL,NULL),(297,'',10,2,NULL,NULL),(298,'',10,2,NULL,NULL),(299,'',10,2,NULL,NULL),(300,'',10,2,NULL,NULL),(301,'',10,2,NULL,NULL),(302,'',10,2,NULL,NULL),(303,'',10,2,NULL,NULL),(304,'',10,2,NULL,NULL),(305,'',10,2,NULL,NULL),(306,'',10,2,NULL,NULL),(307,'',10,2,NULL,NULL),(308,'',10,2,NULL,NULL),(309,'',10,2,NULL,NULL),(310,'',10,2,NULL,NULL),(311,'',10,2,NULL,NULL),(312,'',10,2,NULL,NULL),(313,'',10,2,NULL,NULL),(314,'',10,2,NULL,NULL),(315,'',10,2,NULL,NULL),(316,'',10,2,NULL,NULL),(317,'',10,2,NULL,NULL),(318,'',10,2,NULL,NULL),(319,'',10,2,NULL,NULL),(320,'',10,2,NULL,NULL),(321,'',10,2,NULL,NULL),(322,'',10,2,NULL,NULL),(323,'',10,2,NULL,NULL),(324,'',10,2,NULL,NULL),(325,'',10,2,NULL,NULL),(326,'',10,2,NULL,NULL),(327,'',10,2,NULL,NULL),(328,'',10,2,NULL,NULL),(329,'',10,2,NULL,NULL),(330,'',10,2,NULL,NULL),(331,'',10,2,NULL,NULL),(332,'',10,2,NULL,NULL),(333,'',10,2,NULL,NULL),(334,'',10,2,NULL,NULL),(335,'',10,2,NULL,NULL),(336,'',10,2,NULL,NULL),(337,'',10,2,NULL,NULL),(338,'',10,2,NULL,NULL),(339,'',10,2,NULL,NULL),(340,'',10,2,NULL,NULL),(341,'',10,2,NULL,NULL),(342,'',10,2,NULL,NULL),(343,'',10,2,NULL,NULL),(344,'',10,2,NULL,NULL),(345,'',10,2,NULL,NULL),(346,'',10,2,NULL,NULL),(347,'',10,2,NULL,NULL),(348,'',10,2,NULL,NULL),(349,'',10,2,NULL,NULL),(350,'',10,2,NULL,NULL),(351,'',10,2,NULL,NULL),(352,'',10,2,NULL,NULL),(353,'',10,2,NULL,NULL),(354,'',10,2,NULL,NULL),(355,'',10,2,NULL,NULL),(356,'',10,2,NULL,NULL),(357,'',10,2,NULL,NULL),(358,'',10,2,NULL,NULL),(359,'',10,2,NULL,NULL),(360,'',10,2,NULL,NULL),(361,'',10,2,NULL,NULL),(362,'',10,2,NULL,NULL),(363,'',10,2,NULL,NULL),(364,'',10,2,NULL,NULL),(365,'',10,2,NULL,NULL),(366,'',10,2,NULL,NULL),(367,'',10,2,NULL,NULL),(368,'',10,2,NULL,NULL),(369,'',10,2,NULL,NULL),(370,'',10,2,NULL,NULL),(371,'',10,2,NULL,NULL),(372,'',10,2,NULL,NULL),(373,'',10,2,NULL,NULL),(374,'',10,2,NULL,NULL),(375,'',10,2,NULL,NULL),(376,'',10,2,NULL,NULL),(377,'',10,2,NULL,NULL),(378,'',10,2,NULL,NULL),(379,'',10,2,NULL,NULL),(380,'',10,2,NULL,NULL),(381,'',10,2,NULL,NULL),(382,'',10,2,NULL,NULL),(383,'',10,2,NULL,NULL),(384,'',10,2,NULL,NULL),(385,'',10,2,NULL,NULL),(386,'',10,2,NULL,NULL),(387,'',10,2,NULL,NULL),(388,'',10,2,NULL,NULL),(389,'',10,2,NULL,NULL),(390,'',10,2,NULL,NULL),(391,'',10,2,NULL,NULL),(392,'',10,2,NULL,NULL),(393,'',10,2,NULL,NULL),(394,'',10,2,NULL,NULL),(395,'',10,2,NULL,NULL),(396,'',10,2,NULL,NULL),(397,'',10,2,NULL,NULL),(398,'',10,2,NULL,NULL),(399,'',10,2,NULL,NULL),(400,'',10,2,NULL,NULL),(401,'',10,2,NULL,NULL),(402,'',10,2,NULL,NULL),(403,'',10,2,NULL,NULL),(404,'',10,2,NULL,NULL),(405,'',10,2,NULL,NULL),(406,'',10,2,NULL,NULL),(407,'',10,2,NULL,NULL),(408,'',10,2,NULL,NULL),(409,'',10,2,NULL,NULL),(410,'',10,2,NULL,NULL),(411,'',10,2,NULL,NULL),(412,'',10,2,NULL,NULL),(413,'',10,2,NULL,NULL),(414,'',10,2,NULL,NULL),(415,'',10,2,NULL,NULL),(416,'',10,2,NULL,NULL),(417,'',10,2,NULL,NULL),(418,'',10,2,NULL,NULL),(419,'',10,2,NULL,NULL),(420,'',10,2,NULL,NULL),(421,'',10,2,NULL,NULL),(422,'',10,2,NULL,NULL),(423,'',10,2,NULL,NULL),(424,'',10,2,NULL,NULL),(425,'',10,2,NULL,NULL),(426,'',10,2,NULL,NULL),(427,'',10,2,NULL,NULL),(428,'',10,2,NULL,NULL),(429,'',10,2,NULL,NULL),(430,'',10,2,NULL,NULL),(431,'',10,2,NULL,NULL),(432,'',10,2,NULL,NULL),(433,'',10,2,NULL,NULL),(434,'',10,2,NULL,NULL),(435,'',10,2,NULL,NULL),(436,'',10,2,NULL,NULL),(437,'',10,2,NULL,NULL),(438,'',10,2,NULL,NULL),(439,'',10,2,NULL,NULL),(440,'',10,2,NULL,NULL),(441,'',10,2,NULL,NULL),(442,'',10,2,NULL,NULL),(443,'',10,2,NULL,NULL),(444,'',10,2,NULL,NULL),(445,'',10,2,NULL,NULL),(446,'',10,2,NULL,NULL),(447,'',10,2,NULL,NULL),(448,'',10,2,NULL,NULL),(449,'',10,2,NULL,NULL),(450,'',10,2,NULL,NULL),(451,'',10,2,NULL,NULL),(452,'',10,2,NULL,NULL),(453,'',10,2,NULL,NULL),(454,'',10,2,NULL,NULL),(455,'',10,2,NULL,NULL),(456,'',10,2,NULL,NULL),(457,'',10,2,NULL,NULL),(458,'',10,2,NULL,NULL),(459,'',10,2,NULL,NULL),(460,'',10,2,NULL,NULL),(461,'',10,2,NULL,NULL),(462,'',10,2,NULL,NULL),(463,'',10,2,NULL,NULL),(464,'',10,2,NULL,NULL),(465,'',10,2,NULL,NULL),(466,'',10,2,NULL,NULL),(467,'',10,2,NULL,NULL),(468,'',10,2,NULL,NULL),(469,'',10,2,NULL,NULL),(470,'',10,2,NULL,NULL),(471,'',10,2,NULL,NULL),(472,'',10,2,NULL,NULL),(473,'',10,2,NULL,NULL),(474,'',10,2,NULL,NULL),(475,'',10,2,NULL,NULL),(476,'',10,2,NULL,NULL),(477,'',10,2,NULL,NULL),(478,'',10,2,NULL,NULL),(479,'',10,2,NULL,NULL),(480,'',10,2,NULL,NULL),(481,'',10,2,NULL,NULL),(482,'',10,2,NULL,NULL),(483,'',10,2,NULL,NULL),(484,'',10,2,NULL,NULL),(485,'',10,2,NULL,NULL),(486,'',10,2,NULL,NULL),(487,'',10,2,NULL,NULL),(488,'',10,2,NULL,NULL),(489,'',10,2,NULL,NULL),(490,'',10,2,NULL,NULL),(491,'',10,2,NULL,NULL),(492,'',10,2,NULL,NULL),(493,'',10,2,NULL,NULL),(494,'',10,2,NULL,NULL),(495,'',10,2,NULL,NULL),(496,'',10,2,NULL,NULL),(497,'',10,2,NULL,NULL),(498,'',10,2,NULL,NULL),(499,'',10,2,NULL,NULL),(500,'',10,2,NULL,NULL),(501,'',10,2,NULL,NULL),(502,'',10,2,NULL,NULL),(503,'',10,2,NULL,NULL),(504,'',10,2,NULL,NULL),(505,'',10,2,NULL,NULL),(506,'',10,2,NULL,NULL),(507,'',10,2,NULL,NULL),(508,'',10,2,NULL,NULL),(509,'',10,2,NULL,NULL),(510,'',10,2,NULL,NULL),(511,'',10,2,NULL,NULL),(512,'',10,2,NULL,NULL),(513,'',10,2,NULL,NULL),(514,'',10,2,NULL,NULL),(515,'',10,2,NULL,NULL),(516,'',10,2,NULL,NULL),(517,'',10,2,NULL,NULL),(518,'',10,2,NULL,NULL),(519,'',10,2,NULL,NULL),(520,'',10,2,NULL,NULL),(521,'',10,2,NULL,NULL),(522,'',10,2,NULL,NULL),(523,'',10,2,NULL,NULL),(524,'',10,2,NULL,NULL),(525,'',10,2,NULL,NULL),(526,'',10,2,NULL,NULL),(527,'',10,2,NULL,NULL),(528,'',10,2,NULL,NULL),(529,'',10,2,NULL,NULL),(530,'',10,2,NULL,NULL),(531,'',10,2,NULL,NULL),(532,'',10,2,NULL,NULL),(533,'',10,2,NULL,NULL),(534,'',10,2,NULL,NULL),(535,'',10,2,NULL,NULL),(536,'',10,2,NULL,NULL),(537,'',10,2,NULL,NULL),(538,'',10,2,NULL,NULL),(539,'',10,2,NULL,NULL),(540,'',10,2,NULL,NULL),(541,'',10,2,NULL,NULL),(542,'',10,2,NULL,NULL),(543,'',10,2,NULL,NULL),(544,'',10,2,NULL,NULL),(545,'',10,2,NULL,NULL),(546,'',10,2,NULL,NULL),(547,'',10,2,NULL,NULL),(548,'',10,2,NULL,NULL),(549,'',10,2,NULL,NULL),(550,'',10,2,NULL,NULL),(551,'',10,2,NULL,NULL),(552,'',10,2,NULL,NULL),(553,'',10,2,NULL,NULL),(554,'',10,2,NULL,NULL),(555,'',10,2,NULL,NULL),(556,'',10,2,NULL,NULL),(557,'',10,2,NULL,NULL),(558,'',10,2,NULL,NULL),(559,'',10,2,NULL,NULL),(560,'',10,2,NULL,NULL),(561,'',10,2,NULL,NULL),(562,'',10,2,NULL,NULL),(563,'',10,2,NULL,NULL),(564,'',10,2,NULL,NULL),(565,'',10,2,NULL,NULL),(566,'',10,2,NULL,NULL),(567,'',10,2,NULL,NULL),(568,'',10,2,NULL,NULL),(569,'',10,2,NULL,NULL),(570,'',10,2,NULL,NULL),(571,'',10,2,NULL,NULL),(572,'',10,2,NULL,NULL),(573,'',10,2,NULL,NULL),(574,'',10,2,NULL,NULL),(575,'',10,2,NULL,NULL),(576,'',10,2,NULL,NULL),(577,'',10,2,NULL,NULL),(578,'',10,2,NULL,NULL),(579,'',10,2,NULL,NULL),(580,'',10,2,NULL,NULL),(581,'',10,2,NULL,NULL),(582,'',10,2,NULL,NULL),(583,'',10,2,NULL,NULL),(584,'',10,2,NULL,NULL),(585,'',10,2,NULL,NULL),(586,'',10,2,NULL,NULL),(587,'',10,2,NULL,NULL),(588,'',10,2,NULL,NULL),(589,'',10,2,NULL,NULL),(590,'',10,2,NULL,NULL),(591,'',10,2,NULL,NULL),(592,'',10,2,NULL,NULL),(593,'',10,2,NULL,NULL),(594,'',10,2,NULL,NULL),(595,'',10,2,NULL,NULL),(596,'',10,2,NULL,NULL),(597,'',10,2,NULL,NULL),(598,'',10,2,NULL,NULL),(599,'',10,2,NULL,NULL),(600,'',10,2,NULL,NULL),(601,'',10,2,NULL,NULL),(602,'',10,2,NULL,NULL),(603,'',10,2,NULL,NULL),(604,'',10,2,NULL,NULL),(605,'',10,2,NULL,NULL),(606,'',10,2,NULL,NULL),(607,'',10,2,NULL,NULL),(608,'',10,2,NULL,NULL),(609,'',10,2,NULL,NULL),(610,'',10,2,NULL,NULL),(611,'',10,2,NULL,NULL),(612,'',10,2,NULL,NULL),(613,'',10,2,NULL,NULL),(614,'',10,2,NULL,NULL),(615,'',10,2,NULL,NULL),(616,'',10,2,NULL,NULL),(617,'',10,2,NULL,NULL),(618,'',10,2,NULL,NULL),(619,'',10,2,NULL,NULL),(620,'',10,2,NULL,NULL),(621,'',10,2,NULL,NULL),(622,'',10,2,NULL,NULL),(623,'',10,2,NULL,NULL),(624,'',10,2,NULL,NULL),(625,'',10,2,NULL,NULL),(626,'',10,2,NULL,NULL),(627,'',10,2,NULL,NULL),(628,'',10,2,NULL,NULL),(629,'',10,2,NULL,NULL),(630,'',10,2,NULL,NULL),(631,'',10,2,NULL,NULL),(632,'',10,2,NULL,NULL),(633,'',10,2,NULL,NULL),(634,'',10,2,NULL,NULL),(635,'',10,2,NULL,NULL),(636,'',10,2,NULL,NULL),(637,'',10,2,NULL,NULL),(638,'',10,2,NULL,NULL),(639,'',10,2,NULL,NULL),(640,'',10,2,NULL,NULL),(641,'',10,2,NULL,NULL),(642,'',10,2,NULL,NULL),(643,'',10,2,NULL,NULL),(644,'',10,2,NULL,NULL),(645,'',10,2,NULL,NULL),(646,'',10,2,NULL,NULL),(647,'',10,2,NULL,NULL),(648,'',10,2,NULL,NULL),(649,'',10,2,NULL,NULL),(650,'',10,2,NULL,NULL),(651,'',10,2,NULL,NULL),(652,'',10,2,NULL,NULL),(653,'',10,2,NULL,NULL),(654,'',10,2,NULL,NULL),(655,'',10,2,NULL,NULL),(656,'',10,2,NULL,NULL),(657,'',10,2,NULL,NULL),(658,'',10,2,NULL,NULL),(659,'',10,2,NULL,NULL),(660,'',10,2,NULL,NULL),(661,'',10,2,NULL,NULL),(662,'',10,2,NULL,NULL),(663,'',10,2,NULL,NULL),(664,'',10,2,NULL,NULL),(665,'',10,2,NULL,NULL),(666,'',10,2,NULL,NULL),(667,'',10,2,NULL,NULL),(668,'',10,2,NULL,NULL),(669,'',10,2,NULL,NULL),(670,'',10,2,NULL,NULL),(671,'',10,2,NULL,NULL),(672,'',10,2,NULL,NULL),(673,'',10,2,NULL,NULL),(674,'',10,2,NULL,NULL),(675,'',10,2,NULL,NULL),(676,'',10,2,NULL,NULL),(677,'',10,2,NULL,NULL),(678,'',10,2,NULL,NULL),(679,'',10,2,NULL,NULL),(680,'',10,2,NULL,NULL),(681,'',10,2,NULL,NULL),(682,'',10,2,NULL,NULL),(683,'',10,2,NULL,NULL),(684,'',10,2,NULL,NULL),(685,'',10,2,NULL,NULL),(686,'',10,2,NULL,NULL),(687,'',10,2,NULL,NULL),(688,'',10,2,NULL,NULL),(689,'',10,2,NULL,NULL),(690,'',10,2,NULL,NULL),(691,'',10,2,NULL,NULL),(692,'',10,2,NULL,NULL),(693,'',10,2,NULL,NULL),(694,'',10,2,NULL,NULL),(695,'',10,2,NULL,NULL),(696,'',10,2,NULL,NULL),(697,'',10,2,NULL,NULL),(698,'',10,2,NULL,NULL),(699,'',10,2,NULL,NULL),(700,'',10,2,NULL,NULL),(701,'',10,2,NULL,NULL),(702,'',10,2,NULL,NULL),(703,'',10,2,NULL,NULL),(704,'',10,2,NULL,NULL),(705,'',10,2,NULL,NULL),(706,'',10,2,NULL,NULL),(707,'',10,2,NULL,NULL),(708,'',10,2,NULL,NULL),(709,'',10,2,NULL,NULL),(710,'',10,2,NULL,NULL),(711,'',10,2,NULL,NULL),(712,'',10,2,NULL,NULL),(713,'',10,2,NULL,NULL),(714,'',10,2,NULL,NULL),(715,'',10,2,NULL,NULL),(716,'',10,2,NULL,NULL),(717,'',10,2,NULL,NULL),(718,'',10,2,NULL,NULL),(719,'',10,2,NULL,NULL),(720,'',10,2,NULL,NULL),(721,'',10,2,NULL,NULL),(722,'',10,2,NULL,NULL),(723,'',10,2,NULL,NULL),(724,'',10,2,NULL,NULL),(725,'',10,2,NULL,NULL),(726,'',10,2,NULL,NULL),(727,'',10,2,NULL,NULL),(728,'',10,2,NULL,NULL),(729,'',10,2,NULL,NULL),(730,'',10,2,NULL,NULL),(731,'',10,2,NULL,NULL),(732,'',10,2,NULL,NULL),(733,'',10,2,NULL,NULL),(734,'',10,2,NULL,NULL),(735,'',10,2,NULL,NULL),(736,'',10,2,NULL,NULL),(737,'',10,2,NULL,NULL),(738,'',10,2,NULL,NULL),(739,'',10,2,NULL,NULL),(740,'',10,2,NULL,NULL),(741,'',10,2,NULL,NULL),(742,'',10,2,NULL,NULL),(743,'',10,2,NULL,NULL),(744,'',10,2,NULL,NULL),(745,'',10,2,NULL,NULL),(746,'',10,2,NULL,NULL),(747,'',10,2,NULL,NULL),(748,'',10,2,NULL,NULL),(749,'',10,2,NULL,NULL),(750,'',10,2,NULL,NULL),(751,'',10,2,NULL,NULL),(752,'',10,2,NULL,NULL),(753,'',10,2,NULL,NULL),(754,'',10,2,NULL,NULL),(755,'',10,2,NULL,NULL),(756,'',10,2,NULL,NULL),(757,'',10,2,NULL,NULL),(758,'',10,2,NULL,NULL),(759,'',10,2,NULL,NULL),(760,'',10,2,NULL,NULL),(761,'',10,2,NULL,NULL),(762,'',10,2,NULL,NULL),(763,'',10,2,NULL,NULL),(764,'',10,2,NULL,NULL),(765,'',10,2,NULL,NULL),(766,'',10,2,NULL,NULL),(767,'',10,2,NULL,NULL),(768,'',10,2,NULL,NULL),(769,'',10,2,NULL,NULL),(770,'',10,2,NULL,NULL),(771,'',10,2,NULL,NULL),(772,'',10,2,NULL,NULL),(773,'',10,2,NULL,NULL),(774,'',10,2,NULL,NULL),(775,'',10,2,NULL,NULL),(776,'',10,2,NULL,NULL),(777,'',10,2,NULL,NULL),(778,'',10,2,NULL,NULL),(779,'',10,2,NULL,NULL),(780,'',10,2,NULL,NULL),(781,'',10,2,NULL,NULL),(782,'',10,2,NULL,NULL),(783,'',10,2,NULL,NULL),(784,'',10,2,NULL,NULL),(785,'',10,2,NULL,NULL),(786,'',10,2,NULL,NULL),(787,'',10,2,NULL,NULL),(788,'',10,2,NULL,NULL),(789,'',10,2,NULL,NULL),(790,'',10,2,NULL,NULL),(791,'',10,2,NULL,NULL),(792,'',10,2,NULL,NULL),(793,'',10,2,NULL,NULL),(794,'',10,2,NULL,NULL),(795,'',10,2,NULL,NULL),(796,'',10,2,NULL,NULL),(797,'',10,2,NULL,NULL),(798,'',10,2,NULL,NULL),(799,'',10,2,NULL,NULL),(800,'',10,2,NULL,NULL),(801,'',10,2,NULL,NULL),(802,'',10,2,NULL,NULL),(803,'',10,2,NULL,NULL),(804,'',10,2,NULL,NULL),(805,'',10,2,NULL,NULL),(806,'',10,2,NULL,NULL),(807,'',10,2,NULL,NULL),(808,'',10,2,NULL,NULL),(809,'',10,2,NULL,NULL),(810,'',10,2,NULL,NULL),(811,'',10,2,NULL,NULL),(812,'',10,2,NULL,NULL),(813,'',10,2,NULL,NULL),(814,'',10,2,NULL,NULL),(815,'',10,2,NULL,NULL),(816,'',10,2,NULL,NULL),(817,'',10,2,NULL,NULL),(818,'',10,2,NULL,NULL),(819,'',10,2,NULL,NULL),(820,'',10,2,NULL,NULL),(821,'',10,2,NULL,NULL),(822,'',10,2,NULL,NULL),(823,'',10,2,NULL,NULL),(824,'',10,2,NULL,NULL),(825,'',10,2,NULL,NULL),(826,'',10,2,NULL,NULL),(827,'',10,2,NULL,NULL),(828,'',10,2,NULL,NULL),(829,'',10,2,NULL,NULL),(830,'',10,2,NULL,NULL),(831,'',10,2,NULL,NULL),(832,'',10,2,NULL,NULL),(833,'',10,2,NULL,NULL),(834,'',10,2,NULL,NULL),(835,'',10,2,NULL,NULL),(836,'',10,2,NULL,NULL),(837,'',10,2,NULL,NULL),(838,'',10,2,NULL,NULL),(839,'',10,2,NULL,NULL),(840,'',10,2,NULL,NULL),(841,'',10,2,NULL,NULL),(842,'',10,2,NULL,NULL),(843,'',10,2,NULL,NULL),(844,'',10,2,NULL,NULL),(845,'',10,2,NULL,NULL),(846,'',10,2,NULL,NULL),(847,'',10,2,NULL,NULL),(848,'',10,2,NULL,NULL),(849,'',10,2,NULL,NULL),(850,'',10,2,NULL,NULL),(851,'',10,2,NULL,NULL),(852,'',10,2,NULL,NULL),(853,'',10,2,NULL,NULL),(854,'',10,2,NULL,NULL),(855,'',10,2,NULL,NULL),(856,'',10,2,NULL,NULL),(857,'',10,2,NULL,NULL),(858,'',10,2,NULL,NULL),(859,'',10,2,NULL,NULL),(860,'',10,2,NULL,NULL),(861,'',10,2,NULL,NULL),(862,'',10,2,NULL,NULL),(863,'',10,2,NULL,NULL),(864,'',10,2,NULL,NULL),(865,'',10,2,NULL,NULL),(866,'',10,2,NULL,NULL),(867,'',10,2,NULL,NULL),(868,'',10,2,NULL,NULL),(869,'',10,2,NULL,NULL),(870,'',10,2,NULL,NULL),(871,'',10,2,NULL,NULL),(872,'',10,2,NULL,NULL),(873,'',10,2,NULL,NULL),(874,'',10,2,NULL,NULL),(875,'',10,2,NULL,NULL),(876,'',10,2,NULL,NULL),(877,'',10,2,NULL,NULL),(878,'',10,2,NULL,NULL),(879,'',10,2,NULL,NULL),(880,'',10,2,NULL,NULL),(881,'',10,2,NULL,NULL),(882,'',10,2,NULL,NULL),(883,'',10,2,NULL,NULL),(884,'',10,2,NULL,NULL),(885,'',10,2,NULL,NULL),(886,'',10,2,NULL,NULL),(887,'',10,2,NULL,NULL),(888,'',10,2,NULL,NULL),(889,'',10,2,NULL,NULL),(890,'',10,2,NULL,NULL),(891,'',10,2,NULL,NULL),(892,'',10,2,NULL,NULL),(893,'',10,2,NULL,NULL),(894,'',10,2,NULL,NULL),(895,'',10,2,NULL,NULL),(896,'',10,2,NULL,NULL),(897,'',10,2,NULL,NULL),(898,'',10,2,NULL,NULL),(899,'',10,2,NULL,NULL),(900,'',10,2,NULL,NULL),(901,'',10,2,NULL,NULL),(902,'',10,2,NULL,NULL),(903,'',10,2,NULL,NULL),(904,'',10,2,NULL,NULL),(905,'',10,2,NULL,NULL),(906,'',10,2,NULL,NULL),(907,'',10,2,NULL,NULL),(908,'',10,2,NULL,NULL),(909,'',10,2,NULL,NULL),(910,'',10,2,NULL,NULL),(911,'',10,2,NULL,NULL),(912,'',10,2,NULL,NULL),(913,'',10,2,NULL,NULL),(914,'',10,2,NULL,NULL),(915,'',10,2,NULL,NULL),(916,'',10,2,NULL,NULL),(917,'',10,2,NULL,NULL),(918,'',10,2,NULL,NULL),(919,'',10,2,NULL,NULL),(920,'',10,2,NULL,NULL),(921,'',10,2,NULL,NULL),(922,'',10,2,NULL,NULL),(923,'',10,2,NULL,NULL),(924,'',10,2,NULL,NULL),(925,'',10,2,NULL,NULL),(926,'',10,2,NULL,NULL),(927,'',10,2,NULL,NULL),(928,'',10,2,NULL,NULL),(929,'',10,2,NULL,NULL),(930,'',10,2,NULL,NULL),(931,'',10,2,NULL,NULL),(932,'',10,2,NULL,NULL),(933,'',10,2,NULL,NULL),(934,'',10,2,NULL,NULL),(935,'',10,2,NULL,NULL),(936,'',10,2,NULL,NULL),(937,'',10,2,NULL,NULL),(938,'',10,2,NULL,NULL),(939,'',10,2,NULL,NULL),(940,'',10,2,NULL,NULL),(941,'',10,2,NULL,NULL),(942,'',10,2,NULL,NULL),(943,'',10,2,NULL,NULL),(944,'',10,2,NULL,NULL),(945,'',10,2,NULL,NULL),(946,'',10,2,NULL,NULL),(947,'',10,2,NULL,NULL),(948,'',10,2,NULL,NULL),(949,'',10,2,NULL,NULL),(950,'',10,2,NULL,NULL),(951,'',10,2,NULL,NULL),(952,'',10,2,NULL,NULL),(953,'',10,2,NULL,NULL),(954,'',10,2,NULL,NULL),(955,'',10,2,NULL,NULL),(956,'',10,2,NULL,NULL),(957,'',10,2,NULL,NULL),(958,'',10,2,NULL,NULL),(959,'',10,2,NULL,NULL),(960,'',10,2,NULL,NULL),(961,'',10,2,NULL,NULL),(962,'',10,2,NULL,NULL),(963,'',10,2,NULL,NULL),(964,'',10,2,NULL,NULL),(965,'',10,2,NULL,NULL),(966,'',10,2,NULL,NULL),(967,'',10,2,NULL,NULL),(968,'',10,2,NULL,NULL),(969,'',10,2,NULL,NULL),(970,'',10,2,NULL,NULL),(971,'',10,2,NULL,NULL),(972,'',10,2,NULL,NULL),(973,'',10,2,NULL,NULL),(974,'',10,2,NULL,NULL),(975,'',10,2,NULL,NULL),(976,'',10,2,NULL,NULL),(977,'',10,2,NULL,NULL),(978,'',10,2,NULL,NULL),(979,'',10,2,NULL,NULL),(980,'',10,2,NULL,NULL),(981,'',10,2,NULL,NULL),(982,'',10,2,NULL,NULL),(983,'',10,2,NULL,NULL),(984,'',10,2,NULL,NULL),(985,'',10,2,NULL,NULL),(986,'',10,2,NULL,NULL),(987,'',10,2,NULL,NULL),(988,'',10,2,NULL,NULL),(989,'',10,2,NULL,NULL),(990,'',10,2,NULL,NULL),(991,'',10,2,NULL,NULL),(992,'',10,2,NULL,NULL),(993,'',10,2,NULL,NULL),(994,'',10,2,NULL,NULL),(995,'',10,2,NULL,NULL),(996,'',10,2,NULL,NULL),(997,'',10,2,NULL,NULL),(998,'',10,2,NULL,NULL),(999,'',10,2,NULL,NULL),(1000,'',10,2,NULL,NULL),(1001,'',10,2,NULL,NULL),(1002,'',10,2,NULL,NULL),(1003,'',10,2,NULL,NULL),(1004,'',10,2,NULL,NULL),(1005,'',10,2,NULL,NULL),(1006,'',10,2,NULL,NULL),(1007,'',10,2,NULL,NULL),(1008,'',10,2,NULL,NULL),(1009,'',10,2,NULL,NULL),(1010,'',10,2,NULL,NULL),(1011,'',10,2,NULL,NULL),(1012,'',10,2,NULL,NULL),(1013,'',10,2,NULL,NULL),(1014,'',10,2,NULL,NULL),(1015,'',10,2,NULL,NULL),(1016,'',10,2,NULL,NULL),(1017,'',10,2,NULL,NULL),(1018,'',10,2,NULL,NULL),(1019,'',10,2,NULL,NULL),(1020,'',10,2,NULL,NULL),(1021,'',10,2,NULL,NULL),(1022,'',10,2,NULL,NULL),(1023,'',10,2,NULL,NULL),(1024,'',10,2,NULL,NULL),(1025,'',10,2,NULL,NULL),(1026,'',10,2,NULL,NULL),(1027,'',10,2,NULL,NULL),(1028,'',10,2,NULL,NULL),(1029,'',10,2,NULL,NULL),(1030,'',10,2,NULL,NULL),(1031,'',10,2,NULL,NULL),(1032,'',10,2,NULL,NULL),(1033,'',10,2,NULL,NULL),(1034,'',10,2,NULL,NULL),(1035,'',10,2,NULL,NULL),(1036,'',10,2,NULL,NULL),(1037,'',10,2,NULL,NULL),(1038,'',10,2,NULL,NULL),(1039,'',10,2,NULL,NULL),(1040,'',10,2,NULL,NULL),(1041,'',10,2,NULL,NULL),(1042,'',10,2,NULL,NULL),(1043,'',10,2,NULL,NULL),(1044,'',10,2,NULL,NULL),(1045,'',10,2,NULL,NULL),(1046,'',10,2,NULL,NULL),(1047,'',10,2,NULL,NULL),(1048,'',10,2,NULL,NULL),(1049,'',10,2,NULL,NULL),(1050,'',10,2,NULL,NULL),(1051,'',10,2,NULL,NULL),(1052,'',10,2,NULL,NULL),(1053,'',10,2,NULL,NULL),(1054,'',10,2,NULL,NULL),(1055,'',10,2,NULL,NULL),(1056,'',10,2,NULL,NULL),(1057,'',10,2,NULL,NULL),(1058,'',10,2,NULL,NULL),(1059,'',10,2,NULL,NULL),(1060,'',10,2,NULL,NULL),(1061,'',10,2,NULL,NULL),(1062,'',10,2,NULL,NULL),(1063,'',10,2,NULL,NULL),(1064,'',10,2,NULL,NULL),(1065,'',10,2,NULL,NULL),(1066,'',10,2,NULL,NULL),(1067,'',10,2,NULL,NULL),(1068,'',10,2,NULL,NULL),(1069,'',10,2,NULL,NULL),(1070,'',10,2,NULL,NULL),(1071,'',10,2,NULL,NULL),(1072,'',10,2,NULL,NULL),(1073,'',10,2,NULL,NULL),(1074,'',10,2,NULL,NULL),(1075,'',10,2,NULL,NULL),(1076,'',10,2,NULL,NULL),(1077,'',10,2,NULL,NULL),(1078,'',10,2,NULL,NULL),(1079,'',10,2,NULL,NULL),(1080,'',10,2,NULL,NULL),(1081,'',10,2,NULL,NULL),(1082,'',10,2,NULL,NULL),(1083,'',10,2,NULL,NULL),(1084,'',10,2,NULL,NULL),(1085,'',10,2,NULL,NULL),(1086,'',10,2,NULL,NULL),(1087,'',10,2,NULL,NULL),(1088,'',10,2,NULL,NULL),(1089,'',10,2,NULL,NULL),(1090,'',10,2,NULL,NULL),(1091,'',10,2,NULL,NULL),(1092,'',10,2,NULL,NULL),(1093,'',10,2,NULL,NULL),(1094,'',10,2,NULL,NULL),(1095,'',10,2,NULL,NULL),(1096,'',10,2,NULL,NULL),(1097,'',10,2,NULL,NULL),(1098,'',10,2,NULL,NULL),(1099,'',10,2,NULL,NULL),(1100,'',10,2,NULL,NULL),(1101,'',10,2,NULL,NULL),(1102,'',10,2,NULL,NULL),(1103,'',10,2,NULL,NULL),(1104,'',10,2,NULL,NULL),(1105,'',10,2,NULL,NULL),(1106,'',10,2,NULL,NULL),(1107,'',10,2,NULL,NULL),(1108,'',10,2,NULL,NULL),(1109,'',10,2,NULL,NULL),(1110,'',10,2,NULL,NULL),(1111,'',10,2,NULL,NULL),(1112,'',10,2,NULL,NULL),(1113,'',10,2,NULL,NULL),(1114,'',10,2,NULL,NULL),(1115,'',10,2,NULL,NULL),(1116,'',10,2,NULL,NULL),(1117,'',10,2,NULL,NULL),(1118,'',10,2,NULL,NULL),(1119,'',10,2,NULL,NULL),(1120,'',10,2,NULL,NULL),(1121,'',10,2,NULL,NULL),(1122,'',10,2,NULL,NULL),(1123,'',10,2,NULL,NULL),(1124,'',10,2,NULL,NULL),(1125,'',10,2,NULL,NULL),(1126,'',10,2,NULL,NULL),(1127,'',10,2,NULL,NULL),(1128,'',10,2,NULL,NULL),(1129,'',10,2,NULL,NULL),(1130,'',10,2,NULL,NULL),(1131,'',10,2,NULL,NULL),(1132,'',10,2,NULL,NULL),(1133,'',10,2,NULL,NULL),(1134,'',10,2,NULL,NULL),(1135,'',10,2,NULL,NULL),(1136,'',10,2,NULL,NULL),(1137,'',10,2,NULL,NULL),(1138,'',10,2,NULL,NULL),(1139,'',10,2,NULL,NULL),(1140,'',10,2,NULL,NULL),(1141,'',10,2,NULL,NULL),(1142,'',10,2,NULL,NULL),(1143,'',10,2,NULL,NULL),(1144,'',10,2,NULL,NULL),(1145,'',10,2,NULL,NULL),(1146,'',10,2,NULL,NULL),(1147,'',10,2,NULL,NULL),(1148,'',10,2,NULL,NULL),(1149,'',10,2,NULL,NULL),(1150,'',10,2,NULL,NULL),(1151,'',10,2,NULL,NULL),(1152,'',10,2,NULL,NULL),(1153,'',10,2,NULL,NULL),(1154,'',10,2,NULL,NULL),(1155,'',10,2,NULL,NULL),(1156,'',10,2,NULL,NULL),(1157,'',10,2,NULL,NULL),(1158,'',10,2,NULL,NULL),(1159,'',10,2,NULL,NULL),(1160,'',10,2,NULL,NULL),(1161,'',10,2,NULL,NULL),(1162,'',10,2,NULL,NULL),(1163,'',10,2,NULL,NULL),(1164,'',10,2,NULL,NULL),(1165,'',10,2,NULL,NULL),(1166,'',10,2,NULL,NULL),(1167,'',10,2,NULL,NULL),(1168,'',10,2,NULL,NULL),(1169,'',10,2,NULL,NULL),(1170,'',10,2,NULL,NULL),(1171,'',10,2,NULL,NULL),(1172,'',10,2,NULL,NULL),(1173,'',10,2,NULL,NULL),(1174,'',10,2,NULL,NULL),(1175,'',10,2,NULL,NULL),(1176,'',10,2,NULL,NULL),(1177,'',10,2,NULL,NULL),(1178,'',10,2,NULL,NULL),(1179,'',10,2,NULL,NULL),(1180,'',10,2,NULL,NULL),(1181,'',10,2,NULL,NULL),(1182,'',10,2,NULL,NULL),(1183,'',10,2,NULL,NULL),(1184,'',10,2,NULL,NULL),(1185,'',10,2,NULL,NULL),(1186,'',10,2,NULL,NULL),(1187,'',10,2,NULL,NULL),(1188,'',10,2,NULL,NULL),(1189,'',10,2,NULL,NULL),(1190,'',10,2,NULL,NULL),(1191,'',10,2,NULL,NULL),(1192,'',10,2,NULL,NULL),(1193,'',10,2,NULL,NULL),(1194,'',10,2,NULL,NULL),(1195,'',10,2,NULL,NULL),(1196,'',10,2,NULL,NULL),(1197,'',10,2,NULL,NULL),(1198,'',10,2,NULL,NULL),(1199,'',10,2,NULL,NULL),(1200,'',10,2,NULL,NULL),(1201,'',10,2,NULL,NULL),(1202,'',10,2,NULL,NULL),(1203,'',10,2,NULL,NULL),(1204,'',10,2,NULL,NULL),(1205,'',10,2,NULL,NULL),(1206,'',10,2,NULL,NULL),(1207,'',10,2,NULL,NULL),(1208,'',10,2,NULL,NULL),(1209,'',10,2,NULL,NULL),(1210,'',10,2,NULL,NULL),(1211,'',10,2,NULL,NULL),(1212,'',10,2,NULL,NULL),(1213,'',10,2,NULL,NULL),(1214,'',10,2,NULL,NULL),(1215,'',10,2,NULL,NULL),(1216,'',10,2,NULL,NULL),(1217,'',10,2,NULL,NULL),(1218,'',10,2,NULL,NULL),(1219,'',10,2,NULL,NULL),(1220,'',10,2,NULL,NULL),(1221,'',10,2,NULL,NULL),(1222,'',10,2,NULL,NULL),(1223,'',10,2,NULL,NULL),(1224,'',10,2,NULL,NULL),(1225,'',10,2,NULL,NULL),(1226,'',10,2,NULL,NULL),(1227,'',10,2,NULL,NULL),(1228,'',10,2,NULL,NULL),(1229,'',10,2,NULL,NULL),(1230,'',10,2,NULL,NULL),(1231,'',10,2,NULL,NULL),(1232,'',10,2,NULL,NULL),(1233,'',10,2,NULL,NULL),(1234,'',10,2,NULL,NULL),(1235,'',10,2,NULL,NULL),(1236,'',10,2,NULL,NULL),(1237,'',10,2,NULL,NULL),(1238,'',10,2,NULL,NULL),(1239,'',10,2,NULL,NULL),(1240,'',10,2,NULL,NULL),(1241,'',10,2,NULL,NULL),(1242,'',10,2,NULL,NULL),(1243,'',10,2,NULL,NULL),(1244,'',10,2,NULL,NULL),(1245,'',10,2,NULL,NULL),(1246,'',10,2,NULL,NULL),(1247,'',10,2,NULL,NULL),(1248,'',10,2,NULL,NULL),(1249,'',10,2,NULL,NULL),(1250,'',10,2,NULL,NULL),(1251,'',10,2,NULL,NULL),(1252,'',10,2,NULL,NULL),(1253,'',10,2,NULL,NULL),(1254,'',10,2,NULL,NULL),(1255,'',10,2,NULL,NULL),(1256,'',10,2,NULL,NULL),(1257,'',10,2,NULL,NULL),(1258,'',10,2,NULL,NULL),(1259,'',10,2,NULL,NULL),(1260,'',10,2,NULL,NULL),(1261,'',10,2,NULL,NULL),(1262,'',10,2,NULL,NULL),(1263,'',10,2,NULL,NULL),(1264,'',10,2,NULL,NULL),(1265,'',10,2,NULL,NULL),(1266,'',10,2,NULL,NULL),(1267,'',10,2,NULL,NULL),(1268,'',10,2,NULL,NULL),(1269,'',10,2,NULL,NULL),(1270,'',10,2,NULL,NULL),(1271,'',10,2,NULL,NULL),(1272,'',10,2,NULL,NULL),(1273,'',10,2,NULL,NULL),(1274,'',10,2,NULL,NULL),(1275,'',10,2,NULL,NULL),(1276,'',10,2,NULL,NULL),(1277,'',10,2,NULL,NULL),(1278,'',10,2,NULL,NULL),(1279,'',10,2,NULL,NULL),(1280,'',10,2,NULL,NULL),(1281,'',10,2,NULL,NULL),(1282,'',10,2,NULL,NULL),(1283,'',10,2,NULL,NULL),(1284,'',10,2,NULL,NULL),(1285,'',10,2,NULL,NULL),(1286,'',10,2,NULL,NULL),(1287,'',10,2,NULL,NULL),(1288,'',10,2,NULL,NULL),(1289,'',10,2,NULL,NULL),(1290,'',10,2,NULL,NULL),(1291,'',10,2,NULL,NULL),(1292,'',10,2,NULL,NULL),(1293,'',10,2,NULL,NULL),(1294,'',10,2,NULL,NULL),(1295,'',10,2,NULL,NULL),(1296,'',10,2,NULL,NULL),(1297,'',10,2,NULL,NULL),(1298,'',10,2,NULL,NULL),(1299,'',10,2,NULL,NULL),(1300,'',10,2,NULL,NULL),(1301,'',10,2,NULL,NULL),(1302,'',10,2,NULL,NULL),(1303,'',10,2,NULL,NULL),(1304,'',10,2,NULL,NULL),(1305,'',10,2,NULL,NULL),(1306,'',10,2,NULL,NULL),(1307,'',10,2,NULL,NULL),(1308,'',10,2,NULL,NULL),(1309,'',10,2,NULL,NULL),(1310,'',10,2,NULL,NULL),(1311,'',10,2,NULL,NULL),(1312,'',10,2,NULL,NULL),(1313,'',10,2,NULL,NULL),(1314,'',10,2,NULL,NULL),(1315,'',10,2,NULL,NULL),(1316,'',10,2,NULL,NULL),(1317,'',10,2,NULL,NULL),(1318,'',10,2,NULL,NULL),(1319,'',10,2,NULL,NULL),(1320,'',10,2,NULL,NULL),(1321,'',10,2,NULL,NULL),(1322,'',10,2,NULL,NULL),(1323,'',10,2,NULL,NULL),(1324,'',10,2,NULL,NULL),(1325,'',10,2,NULL,NULL),(1326,'',10,2,NULL,NULL),(1327,'',10,2,NULL,NULL),(1328,'',10,2,NULL,NULL),(1329,'',10,2,NULL,NULL),(1330,'',10,2,NULL,NULL),(1331,'',10,2,NULL,NULL),(1332,'',10,2,NULL,NULL),(1333,'',10,2,NULL,NULL),(1334,'',10,2,NULL,NULL),(1335,'',10,2,NULL,NULL),(1336,'',10,2,NULL,NULL),(1337,'',10,2,NULL,NULL),(1338,'',10,2,NULL,NULL),(1339,'',10,2,NULL,NULL),(1340,'',10,2,NULL,NULL),(1341,'',10,2,NULL,NULL),(1342,'',10,2,NULL,NULL),(1343,'',10,2,NULL,NULL),(1344,'',10,2,NULL,NULL),(1345,'',10,2,NULL,NULL),(1346,'',10,2,NULL,NULL),(1347,'',10,2,NULL,NULL),(1348,'',10,2,NULL,NULL),(1349,'',10,2,NULL,NULL),(1350,'',10,2,NULL,NULL),(1351,'',10,2,NULL,NULL),(1352,'',10,2,NULL,NULL),(1353,'',10,2,NULL,NULL),(1354,'',10,2,NULL,NULL),(1355,'',10,2,NULL,NULL),(1356,'',10,2,NULL,NULL),(1357,'',10,2,NULL,NULL),(1358,'',10,2,NULL,NULL),(1359,'',10,2,NULL,NULL),(1360,'',10,2,NULL,NULL),(1361,'',10,2,NULL,NULL),(1362,'',10,2,NULL,NULL),(1363,'',10,2,NULL,NULL),(1364,'',10,2,NULL,NULL),(1365,'',10,2,NULL,NULL),(1366,'',10,2,NULL,NULL),(1367,'',10,2,NULL,NULL),(1368,'',10,2,NULL,NULL),(1369,'',10,2,NULL,NULL),(1370,'',10,2,NULL,NULL),(1371,'',10,2,NULL,NULL),(1372,'',10,2,NULL,NULL),(1373,'',10,2,NULL,NULL),(1374,'',10,2,NULL,NULL),(1375,'',10,2,NULL,NULL),(1376,'',10,2,NULL,NULL),(1377,'',10,2,NULL,NULL),(1378,'',10,2,NULL,NULL),(1379,'',10,2,NULL,NULL),(1380,'',10,2,NULL,NULL),(1381,'',10,2,NULL,NULL),(1382,'',10,2,NULL,NULL),(1383,'',10,2,NULL,NULL),(1384,'',10,2,NULL,NULL),(1385,'',10,2,NULL,NULL),(1386,'',10,2,NULL,NULL),(1387,'',10,2,NULL,NULL),(1388,'',10,2,NULL,NULL),(1389,'',10,2,NULL,NULL),(1390,'',10,2,NULL,NULL),(1391,'',10,2,NULL,NULL),(1392,'',10,2,NULL,NULL),(1393,'',10,2,NULL,NULL),(1394,'',10,2,NULL,NULL),(1395,'',10,2,NULL,NULL),(1396,'',10,2,NULL,NULL),(1397,'',10,2,NULL,NULL),(1398,'',10,2,NULL,NULL),(1399,'',10,2,NULL,NULL),(1400,'',10,2,NULL,NULL),(1401,'',10,2,NULL,NULL),(1402,'',10,2,NULL,NULL),(1403,'',10,2,NULL,NULL),(1404,'',10,2,NULL,NULL),(1405,'',10,2,NULL,NULL),(1406,'',10,2,NULL,NULL),(1407,'',10,2,NULL,NULL),(1408,'',10,2,NULL,NULL),(1409,'',10,2,NULL,NULL),(1410,'',10,2,NULL,NULL),(1411,'',10,2,NULL,NULL),(1412,'',10,2,NULL,NULL),(1413,'',10,2,NULL,NULL),(1414,'',10,2,NULL,NULL),(1415,'',10,2,NULL,NULL),(1416,'',10,2,NULL,NULL),(1417,'',10,2,NULL,NULL),(1418,'',10,2,NULL,NULL),(1419,'',10,2,NULL,NULL),(1420,'',10,2,NULL,NULL),(1421,'',10,2,NULL,NULL),(1422,'',10,2,NULL,NULL),(1423,'',10,2,NULL,NULL),(1424,'',10,2,NULL,NULL),(1425,'',10,2,NULL,NULL),(1426,'',10,2,NULL,NULL),(1427,'',10,2,NULL,NULL),(1428,'',10,2,NULL,NULL),(1429,'',10,2,NULL,NULL),(1430,'',10,2,NULL,NULL),(1431,'',10,2,NULL,NULL),(1432,'',10,2,NULL,NULL),(1433,'',10,2,NULL,NULL),(1434,'',10,2,NULL,NULL),(1435,'',10,2,NULL,NULL),(1436,'',10,2,NULL,NULL),(1437,'',10,2,NULL,NULL),(1438,'',10,2,NULL,NULL),(1439,'',10,2,NULL,NULL),(1440,'',10,2,NULL,NULL),(1441,'',10,2,NULL,NULL),(1442,'',10,2,NULL,NULL),(1443,'',10,2,NULL,NULL),(1444,'',10,2,NULL,NULL),(1445,'',10,2,NULL,NULL),(1446,'',10,2,NULL,NULL),(1447,'',10,2,NULL,NULL),(1448,'',10,2,NULL,NULL),(1449,'',10,2,NULL,NULL),(1450,'',10,2,NULL,NULL),(1451,'',10,2,NULL,NULL),(1452,'',10,2,NULL,NULL),(1453,'',10,2,NULL,NULL),(1454,'',10,2,NULL,NULL),(1455,'',10,2,NULL,NULL),(1456,'',10,2,NULL,NULL),(1457,'',10,2,NULL,NULL),(1458,'',10,2,NULL,NULL),(1459,'',10,2,NULL,NULL),(1460,'',10,2,NULL,NULL),(1461,'',10,2,NULL,NULL),(1462,'',10,2,NULL,NULL),(1463,'',10,2,NULL,NULL),(1464,'',10,2,NULL,NULL),(1465,'',10,2,NULL,NULL),(1466,'',10,2,NULL,NULL),(1467,'',10,2,NULL,NULL),(1468,'',10,2,NULL,NULL),(1469,'',10,2,NULL,NULL),(1470,'',10,2,NULL,NULL),(1471,'',10,2,NULL,NULL),(1472,'',10,2,NULL,NULL),(1473,'',10,2,NULL,NULL),(1474,'',10,2,NULL,NULL),(1475,'',10,2,NULL,NULL),(1476,'',10,2,NULL,NULL),(1477,'',10,2,NULL,NULL),(1478,'',10,2,NULL,NULL),(1479,'',10,2,NULL,NULL),(1480,'',10,2,NULL,NULL),(1481,'',10,2,NULL,NULL),(1482,'',10,2,NULL,NULL),(1483,'',10,2,NULL,NULL),(1484,'',10,2,NULL,NULL),(1485,'',10,2,NULL,NULL),(1486,'',10,2,NULL,NULL),(1487,'',10,2,NULL,NULL),(1488,'',10,2,NULL,NULL),(1489,'',10,2,NULL,NULL),(1490,'',10,2,NULL,NULL),(1491,'',10,2,NULL,NULL),(1492,'',10,2,NULL,NULL),(1493,'',10,2,NULL,NULL),(1494,'',10,2,NULL,NULL),(1495,'',10,2,NULL,NULL),(1496,'',10,2,NULL,NULL),(1497,'',10,2,NULL,NULL),(1498,'',10,2,NULL,NULL),(1499,'',10,2,NULL,NULL),(1500,'',10,2,NULL,NULL),(1501,'',10,2,NULL,NULL),(1502,'',10,2,NULL,NULL),(1503,'',10,2,NULL,NULL),(1504,'',10,2,NULL,NULL),(1505,'',10,2,NULL,NULL),(1506,'',10,2,NULL,NULL),(1507,'',10,2,NULL,NULL),(1508,'',10,2,NULL,NULL),(1509,'',10,2,NULL,NULL),(1510,'',10,2,NULL,NULL),(1511,'',10,2,NULL,NULL),(1512,'',10,2,NULL,NULL),(1513,'',10,2,NULL,NULL),(1514,'',10,2,NULL,NULL),(1515,'',10,2,NULL,NULL),(1516,'',10,2,NULL,NULL),(1517,'',10,2,NULL,NULL),(1518,'',10,2,NULL,NULL),(1519,'',10,2,NULL,NULL),(1520,'',10,2,NULL,NULL),(1521,'',10,2,NULL,NULL),(1522,'',10,2,NULL,NULL),(1523,'',10,2,NULL,NULL),(1524,'',10,2,NULL,NULL),(1525,'',10,2,NULL,NULL),(1526,'',10,2,NULL,NULL),(1527,'',10,2,NULL,NULL),(1528,'',10,2,NULL,NULL),(1529,'',10,2,NULL,NULL),(1530,'',10,2,NULL,NULL),(1531,'',10,2,NULL,NULL),(1532,'',10,2,NULL,NULL),(1533,'',10,2,NULL,NULL),(1534,'',10,2,NULL,NULL),(1535,'',10,2,NULL,NULL),(1536,'',10,2,NULL,NULL),(1537,'',10,2,NULL,NULL),(1538,'',10,2,NULL,NULL),(1539,'',10,2,NULL,NULL),(1540,'',10,2,NULL,NULL),(1541,'',10,2,NULL,NULL),(1542,'',10,2,NULL,NULL),(1543,'',10,2,NULL,NULL),(1544,'',10,2,NULL,NULL),(1545,'',10,2,NULL,NULL),(1546,'',10,2,NULL,NULL),(1547,'',10,2,NULL,NULL),(1548,'',10,2,NULL,NULL),(1549,'',10,2,NULL,NULL),(1550,'',10,2,NULL,NULL),(1551,'',10,2,NULL,NULL),(1552,'',10,2,NULL,NULL),(1553,'',10,2,NULL,NULL),(1554,'',10,2,NULL,NULL),(1555,'',10,2,NULL,NULL),(1556,'',10,2,NULL,NULL),(1557,'',10,2,NULL,NULL),(1558,'',10,2,NULL,NULL),(1559,'',10,2,NULL,NULL),(1560,'',10,2,NULL,NULL),(1561,'',10,2,NULL,NULL),(1562,'',10,2,NULL,NULL),(1563,'',10,2,NULL,NULL),(1564,'',10,2,NULL,NULL),(1565,'',10,2,NULL,NULL),(1566,'',10,2,NULL,NULL),(1567,'',10,2,NULL,NULL),(1568,'',10,2,NULL,NULL),(1569,'',10,2,NULL,NULL),(1570,'',10,2,NULL,NULL),(1571,'',10,2,NULL,NULL),(1572,'',10,2,NULL,NULL),(1573,'',10,2,NULL,NULL),(1574,'',10,2,NULL,NULL),(1575,'',10,2,NULL,NULL),(1576,'',10,2,NULL,NULL),(1577,'',10,2,NULL,NULL),(1578,'',10,2,NULL,NULL),(1579,'',10,2,NULL,NULL),(1580,'',10,2,NULL,NULL),(1581,'',10,2,NULL,NULL),(1582,'',10,2,NULL,NULL),(1583,'',10,2,NULL,NULL),(1584,'',10,2,NULL,NULL),(1585,'',10,2,NULL,NULL),(1586,'',10,2,NULL,NULL),(1587,'',10,2,NULL,NULL),(1588,'',10,2,NULL,NULL),(1589,'',10,2,NULL,NULL),(1590,'',10,2,NULL,NULL),(1591,'',10,2,NULL,NULL),(1592,'',10,2,NULL,NULL),(1593,'',10,2,NULL,NULL),(1594,'',10,2,NULL,NULL),(1595,'',10,2,NULL,NULL),(1596,'',10,2,NULL,NULL),(1597,'',10,2,NULL,NULL),(1598,'',10,2,NULL,NULL),(1599,'',10,2,NULL,NULL),(1600,'',10,2,NULL,NULL),(1601,'',10,2,NULL,NULL),(1602,'',10,2,NULL,NULL),(1603,'',10,2,NULL,NULL),(1604,'',10,2,NULL,NULL),(1605,'',10,2,NULL,NULL),(1606,'',10,2,NULL,NULL),(1607,'',10,2,NULL,NULL),(1608,'',10,2,NULL,NULL),(1609,'',10,2,NULL,NULL),(1610,'',10,2,NULL,NULL),(1611,'',10,2,NULL,NULL),(1612,'',10,2,NULL,NULL),(1613,'',10,2,NULL,NULL),(1614,'',10,2,NULL,NULL),(1615,'',10,2,NULL,NULL),(1616,'',10,2,NULL,NULL),(1617,'',10,2,NULL,NULL),(1618,'',10,2,NULL,NULL),(1619,'',10,2,NULL,NULL),(1620,'',10,2,NULL,NULL),(1621,'',10,2,NULL,NULL),(1622,'',10,2,NULL,NULL),(1623,'',10,2,NULL,NULL),(1624,'',10,2,NULL,NULL),(1625,'',10,2,NULL,NULL),(1626,'',10,2,NULL,NULL),(1627,'',10,2,NULL,NULL),(1628,'',10,2,NULL,NULL),(1629,'',10,2,NULL,NULL),(1630,'',10,2,NULL,NULL),(1631,'',10,2,NULL,NULL),(1632,'',10,2,NULL,NULL),(1633,'',10,2,NULL,NULL),(1634,'',10,2,NULL,NULL),(1635,'',10,2,NULL,NULL),(1636,'',10,2,NULL,NULL),(1637,'',10,2,NULL,NULL),(1638,'',10,2,NULL,NULL),(1639,'',10,2,NULL,NULL),(1640,'',10,2,NULL,NULL),(1641,'',10,2,NULL,NULL),(1642,'',10,2,NULL,NULL),(1643,'',10,2,NULL,NULL),(1644,'',10,2,NULL,NULL),(1645,'',10,2,NULL,NULL),(1646,'',10,2,NULL,NULL),(1647,'',10,2,NULL,NULL),(1648,'',10,2,NULL,NULL),(1649,'',10,2,NULL,NULL),(1650,'',10,2,NULL,NULL),(1651,'',10,2,NULL,NULL),(1652,'',10,2,NULL,NULL),(1653,'',10,2,NULL,NULL),(1654,'',10,2,NULL,NULL),(1655,'',10,2,NULL,NULL),(1656,'',10,2,NULL,NULL),(1657,'',10,2,NULL,NULL),(1658,'',10,2,NULL,NULL),(1659,'',10,2,NULL,NULL),(1660,'',10,2,NULL,NULL),(1661,'',10,2,NULL,NULL),(1662,'',10,2,NULL,NULL),(1663,'',10,2,NULL,NULL),(1664,'',10,2,NULL,NULL),(1665,'',10,2,NULL,NULL),(1666,'',10,2,NULL,NULL),(1667,'',10,2,NULL,NULL),(1668,'',10,2,NULL,NULL),(1669,'',10,2,NULL,NULL),(1670,'',10,2,NULL,NULL),(1671,'',10,2,NULL,NULL),(1672,'',10,2,NULL,NULL),(1673,'',10,2,NULL,NULL),(1674,'',10,2,NULL,NULL),(1675,'',10,2,NULL,NULL),(1676,'',10,2,NULL,NULL),(1677,'',10,2,NULL,NULL),(1678,'',10,2,NULL,NULL),(1679,'',10,2,NULL,NULL),(1680,'',10,2,NULL,NULL),(1681,'',10,2,NULL,NULL),(1682,'',10,2,NULL,NULL),(1683,'',10,2,NULL,NULL),(1684,'',10,2,NULL,NULL),(1685,'',10,2,NULL,NULL),(1686,'',10,2,NULL,NULL),(1687,'',10,2,NULL,NULL),(1688,'',10,2,NULL,NULL),(1689,'',10,2,NULL,NULL),(1690,'',10,2,NULL,NULL),(1691,'',10,2,NULL,NULL),(1692,'',10,2,NULL,NULL),(1693,'',10,2,NULL,NULL),(1694,'',10,2,NULL,NULL),(1695,'',10,2,NULL,NULL),(1696,'',10,2,NULL,NULL),(1697,'',10,2,NULL,NULL),(1698,'',10,2,NULL,NULL),(1699,'',10,2,NULL,NULL),(1700,'',10,2,NULL,NULL),(1701,'',10,2,NULL,NULL),(1702,'',10,2,NULL,NULL),(1703,'',10,2,NULL,NULL),(1704,'',10,2,NULL,NULL),(1705,'',10,2,NULL,NULL),(1706,'',10,2,NULL,NULL),(1707,'',10,2,NULL,NULL),(1708,'',10,2,NULL,NULL),(1709,'',10,2,NULL,NULL),(1710,'',10,2,NULL,NULL),(1711,'',10,2,NULL,NULL),(1712,'',10,2,NULL,NULL),(1713,'',10,2,NULL,NULL),(1714,'',10,2,NULL,NULL),(1715,'',10,2,NULL,NULL),(1716,'',10,2,NULL,NULL),(1717,'',10,2,NULL,NULL),(1718,'',10,2,NULL,NULL),(1719,'',10,2,NULL,NULL),(1720,'',10,2,NULL,NULL),(1721,'',10,2,NULL,NULL),(1722,'',10,2,NULL,NULL),(1723,'',10,2,NULL,NULL),(1724,'',10,2,NULL,NULL),(1725,'',10,2,NULL,NULL),(1726,'',10,2,NULL,NULL),(1727,'',10,2,NULL,NULL),(1728,'',10,2,NULL,NULL),(1729,'',10,2,NULL,NULL),(1730,'',10,2,NULL,NULL),(1731,'',10,2,NULL,NULL),(1732,'',10,2,NULL,NULL),(1733,'',10,2,NULL,NULL),(1734,'',10,2,NULL,NULL),(1735,'',10,2,NULL,NULL),(1736,'',10,2,NULL,NULL),(1737,'',10,2,NULL,NULL),(1738,'',10,2,NULL,NULL),(1739,'',10,2,NULL,NULL),(1740,'',10,2,NULL,NULL),(1741,'',10,2,NULL,NULL),(1742,'',10,2,NULL,NULL),(1743,'',10,2,NULL,NULL),(1744,'',10,2,NULL,NULL),(1745,'',10,2,NULL,NULL),(1746,'',10,2,NULL,NULL),(1747,'',10,2,NULL,NULL),(1748,'',10,2,NULL,NULL),(1749,'',10,2,NULL,NULL),(1750,'',10,2,NULL,NULL),(1751,'',10,2,NULL,NULL),(1752,'',10,2,NULL,NULL),(1753,'',10,2,NULL,NULL),(1754,'',10,2,NULL,NULL),(1755,'',10,2,NULL,NULL),(1756,'',10,2,NULL,NULL),(1757,'',10,2,NULL,NULL),(1758,'',10,2,NULL,NULL),(1759,'',10,2,NULL,NULL),(1760,'',10,2,NULL,NULL),(1761,'',10,2,NULL,NULL),(1762,'',10,2,NULL,NULL),(1763,'',10,2,NULL,NULL),(1764,'',10,2,NULL,NULL),(1765,'',10,2,NULL,NULL),(1766,'',10,2,NULL,NULL),(1767,'',10,2,NULL,NULL),(1768,'',10,2,NULL,NULL),(1769,'',10,2,NULL,NULL),(1770,'',10,2,NULL,NULL),(1771,'',10,2,NULL,NULL),(1772,'',10,2,NULL,NULL),(1773,'',10,2,NULL,NULL),(1774,'',10,2,NULL,NULL),(1775,'',10,2,NULL,NULL),(1776,'',10,2,NULL,NULL),(1777,'',10,2,NULL,NULL),(1778,'',10,2,NULL,NULL),(1779,'',10,2,NULL,NULL),(1780,'',10,2,NULL,NULL),(1781,'',10,2,NULL,NULL),(1782,'',10,2,NULL,NULL),(1783,'',10,2,NULL,NULL),(1784,'',10,2,NULL,NULL),(1785,'',10,2,NULL,NULL),(1786,'',10,2,NULL,NULL),(1787,'',10,2,NULL,NULL),(1788,'',10,2,NULL,NULL),(1789,'',10,2,NULL,NULL),(1790,'',10,2,NULL,NULL),(1791,'',10,2,NULL,NULL),(1792,'',10,2,NULL,NULL),(1793,'',10,2,NULL,NULL),(1794,'',10,2,NULL,NULL),(1795,'',10,2,NULL,NULL),(1796,'',10,2,NULL,NULL),(1797,'',10,2,NULL,NULL),(1798,'',10,2,NULL,NULL),(1799,'',10,2,NULL,NULL),(1800,'',10,2,NULL,NULL),(1801,'',10,2,NULL,NULL),(1802,'',10,2,NULL,NULL),(1803,'',10,2,NULL,NULL),(1804,'',10,2,NULL,NULL),(1805,'',10,2,NULL,NULL),(1806,'',10,2,NULL,NULL),(1807,'',10,2,NULL,NULL),(1808,'',10,2,NULL,NULL),(1809,'',10,2,NULL,NULL),(1810,'',10,2,NULL,NULL),(1811,'',10,2,NULL,NULL),(1812,'',10,2,NULL,NULL),(1813,'',10,2,NULL,NULL),(1814,'',10,2,NULL,NULL),(1815,'',10,2,NULL,NULL),(1816,'',10,2,NULL,NULL),(1817,'',10,2,NULL,NULL),(1818,'',10,2,NULL,NULL),(1819,'',10,2,NULL,NULL),(1820,'',10,2,NULL,NULL),(1821,'',10,2,NULL,NULL),(1822,'',10,2,NULL,NULL),(1823,'',10,2,NULL,NULL),(1824,'',10,2,NULL,NULL),(1825,'',10,2,NULL,NULL),(1826,'',10,2,NULL,NULL),(1827,'',10,2,NULL,NULL),(1828,'',10,2,NULL,NULL),(1829,'',10,2,NULL,NULL),(1830,'',10,2,NULL,NULL),(1831,'',10,2,NULL,NULL),(1832,'',10,2,NULL,NULL),(1833,'',10,2,NULL,NULL),(1834,'',10,2,NULL,NULL),(1835,'',10,2,NULL,NULL),(1836,'',10,2,NULL,NULL),(1837,'',10,2,NULL,NULL),(1838,'',10,2,NULL,NULL),(1839,'',10,2,NULL,NULL),(1840,'',10,2,NULL,NULL),(1841,'',10,2,NULL,NULL),(1842,'',10,2,NULL,NULL),(1843,'',10,2,NULL,NULL),(1844,'',10,2,NULL,NULL),(1845,'',10,2,NULL,NULL),(1846,'',10,2,NULL,NULL),(1847,'',10,2,NULL,NULL),(1848,'',10,2,NULL,NULL),(1849,'',10,2,NULL,NULL),(1850,'',10,2,NULL,NULL),(1851,'',10,2,NULL,NULL),(1852,'',10,2,NULL,NULL),(1853,'',10,2,NULL,NULL),(1854,'',10,2,NULL,NULL),(1855,'',10,2,NULL,NULL),(1856,'',10,2,NULL,NULL),(1857,'',10,2,NULL,NULL),(1858,'',10,2,NULL,NULL),(1859,'',10,2,NULL,NULL),(1860,'',10,2,NULL,NULL),(1861,'',10,2,NULL,NULL),(1862,'',10,2,NULL,NULL),(1863,'',10,2,NULL,NULL),(1864,'',10,2,NULL,NULL),(1865,'',10,2,NULL,NULL),(1866,'',10,2,NULL,NULL),(1867,'',10,2,NULL,NULL),(1868,'',10,2,NULL,NULL),(1869,'',10,2,NULL,NULL),(1870,'',10,2,NULL,NULL),(1871,'',10,2,NULL,NULL),(1872,'',10,2,NULL,NULL),(1873,'',10,2,NULL,NULL),(1874,'',10,2,NULL,NULL),(1875,'',10,2,NULL,NULL),(1876,'',10,2,NULL,NULL),(1877,'',10,2,NULL,NULL),(1878,'',10,2,NULL,NULL),(1879,'',10,2,NULL,NULL),(1880,'',10,2,NULL,NULL),(1881,'',10,2,NULL,NULL),(1882,'',10,2,NULL,NULL),(1883,'',10,2,NULL,NULL),(1884,'',10,2,NULL,NULL),(1885,'',10,2,NULL,NULL),(1886,'',10,2,NULL,NULL),(1887,'',10,2,NULL,NULL),(1888,'',10,2,NULL,NULL),(1889,'',10,2,NULL,NULL),(1890,'',10,2,NULL,NULL),(1891,'',10,2,NULL,NULL),(1892,'',10,2,NULL,NULL),(1893,'',10,2,NULL,NULL),(1894,'',10,2,NULL,NULL),(1895,'',10,2,NULL,NULL),(1896,'',10,2,NULL,NULL),(1897,'',10,2,NULL,NULL),(1898,'',10,2,NULL,NULL),(1899,'',10,2,NULL,NULL),(1900,'',10,2,NULL,NULL),(1901,'',10,2,NULL,NULL),(1902,'',10,2,NULL,NULL),(1903,'',10,2,NULL,NULL),(1904,'',10,2,NULL,NULL),(1905,'',10,2,NULL,NULL),(1906,'',10,2,NULL,NULL),(1907,'',10,2,NULL,NULL),(1908,'',10,2,NULL,NULL),(1909,'',10,2,NULL,NULL),(1910,'',10,2,NULL,NULL),(1911,'',10,2,NULL,NULL),(1912,'',10,2,NULL,NULL),(1913,'',10,2,NULL,NULL),(1914,'',10,2,NULL,NULL),(1915,'',10,2,NULL,NULL),(1916,'',10,2,NULL,NULL),(1917,'',10,2,NULL,NULL),(1918,'',10,2,NULL,NULL),(1919,'',10,2,NULL,NULL),(1920,'',10,2,NULL,NULL),(1921,'',10,2,NULL,NULL),(1922,'',10,2,NULL,NULL),(1923,'',10,2,NULL,NULL),(1924,'',10,2,NULL,NULL),(1925,'',10,2,NULL,NULL),(1926,'',10,2,NULL,NULL),(1927,'',10,2,NULL,NULL),(1928,'',10,2,NULL,NULL),(1929,'',10,2,NULL,NULL),(1930,'',10,2,NULL,NULL),(1931,'',10,2,NULL,NULL),(1932,'',10,2,NULL,NULL),(1933,'',10,2,NULL,NULL),(1934,'',10,2,NULL,NULL),(1935,'',10,2,NULL,NULL),(1936,'',10,2,NULL,NULL),(1937,'',10,2,NULL,NULL),(1938,'',10,2,NULL,NULL),(1939,'',10,2,NULL,NULL),(1940,'',10,2,NULL,NULL),(1941,'',10,2,NULL,NULL),(1942,'',10,2,NULL,NULL),(1943,'',10,2,NULL,NULL),(1944,'',10,2,NULL,NULL),(1945,'',10,2,NULL,NULL),(1946,'',10,2,NULL,NULL),(1947,'',10,2,NULL,NULL),(1948,'',10,2,NULL,NULL),(1949,'',10,2,NULL,NULL),(1950,'',10,2,NULL,NULL),(1951,'',10,2,NULL,NULL),(1952,'',10,2,NULL,NULL),(1953,'',10,2,NULL,NULL),(1954,'',10,2,NULL,NULL),(1955,'',10,2,NULL,NULL),(1956,'',10,2,NULL,NULL),(1957,'',10,2,NULL,NULL),(1958,'',10,2,NULL,NULL),(1959,'',10,2,NULL,NULL),(1960,'',10,2,NULL,NULL),(1961,'',10,2,NULL,NULL),(1962,'',10,2,NULL,NULL),(1963,'',10,2,NULL,NULL),(1964,'',10,2,NULL,NULL),(1965,'',10,2,NULL,NULL),(1966,'',10,2,NULL,NULL),(1967,'',10,2,NULL,NULL),(1968,'',10,2,NULL,NULL),(1969,'',10,2,NULL,NULL),(1970,'',10,2,NULL,NULL),(1971,'',10,2,NULL,NULL),(1972,'',10,2,NULL,NULL),(1973,'',10,2,NULL,NULL),(1974,'',10,2,NULL,NULL),(1975,'',10,2,NULL,NULL),(1976,'',10,2,NULL,NULL),(1977,'',10,2,NULL,NULL),(1978,'',10,2,NULL,NULL),(1979,'',10,2,NULL,NULL),(1980,'',10,2,NULL,NULL),(1981,'',10,2,NULL,NULL),(1982,'',10,2,NULL,NULL),(1983,'',10,2,NULL,NULL),(1984,'',10,2,NULL,NULL),(1985,'',10,2,NULL,NULL),(1986,'',10,2,NULL,NULL),(1987,'',10,2,NULL,NULL),(1988,'',10,2,NULL,NULL),(1989,'',10,2,NULL,NULL),(1990,'',10,2,NULL,NULL),(1991,'',10,2,NULL,NULL),(1992,'',10,2,NULL,NULL),(1993,'',10,2,NULL,NULL),(1994,'',10,2,NULL,NULL),(1995,'',10,2,NULL,NULL),(1996,'',10,2,NULL,NULL),(1997,'',10,2,NULL,NULL),(1998,'',10,2,NULL,NULL),(1999,'',10,2,NULL,NULL),(2000,'',10,2,NULL,NULL),(2001,'',10,2,NULL,NULL),(2002,'',10,2,NULL,NULL),(2003,'',10,2,NULL,NULL),(2004,'',10,2,NULL,NULL),(2005,'',10,2,NULL,NULL),(2006,'',10,2,NULL,NULL),(2007,'',10,2,NULL,NULL),(2008,'',10,2,NULL,NULL),(2009,'',10,2,NULL,NULL),(2010,'',10,2,NULL,NULL),(2011,'',10,2,NULL,NULL),(2012,'',10,2,NULL,NULL),(2013,'',10,2,NULL,NULL),(2014,'',10,2,NULL,NULL),(2015,'',10,2,NULL,NULL),(2016,'',10,2,NULL,NULL),(2017,'',10,2,NULL,NULL),(2018,'',10,2,NULL,NULL),(2019,'',10,2,NULL,NULL),(2020,'',10,2,NULL,NULL),(2021,'',10,2,NULL,NULL),(2022,'',10,2,NULL,NULL),(2023,'',10,2,NULL,NULL),(2024,'',10,2,NULL,NULL),(2025,'',10,2,NULL,NULL),(2026,'',10,2,NULL,NULL),(2027,'',10,2,NULL,NULL),(2028,'',10,2,NULL,NULL),(2029,'',10,2,NULL,NULL),(2030,'',10,2,NULL,NULL),(2031,'',10,2,NULL,NULL),(2032,'',10,2,NULL,NULL),(2033,'',10,2,NULL,NULL),(2034,'',10,2,NULL,NULL),(2035,'',10,2,NULL,NULL),(2036,'',10,2,NULL,NULL),(2037,'',10,2,NULL,NULL),(2038,'',10,2,NULL,NULL),(2039,'',10,2,NULL,NULL),(2040,'',10,2,NULL,NULL),(2041,'',10,2,NULL,NULL),(2042,'',10,2,NULL,NULL),(2043,'',10,2,NULL,NULL),(2044,'',10,2,NULL,NULL),(2045,'',10,2,NULL,NULL),(2046,'',10,2,NULL,NULL),(2047,'',10,2,NULL,NULL),(2048,'',10,2,NULL,NULL),(2049,'',10,2,NULL,NULL),(2050,'',10,2,NULL,NULL),(2051,'',10,2,NULL,NULL),(2052,'',10,2,NULL,NULL),(2053,'',10,2,NULL,NULL),(2054,'',10,2,NULL,NULL),(2055,'',10,2,NULL,NULL),(2056,'',10,2,NULL,NULL),(2057,'',10,2,NULL,NULL),(2058,'',10,2,NULL,NULL),(2059,'',10,2,NULL,NULL),(2060,'',10,2,NULL,NULL),(2061,'',10,2,NULL,NULL),(2062,'',10,2,NULL,NULL),(2063,'',10,2,NULL,NULL),(2064,'',10,2,NULL,NULL),(2065,'',10,2,NULL,NULL),(2066,'',10,2,NULL,NULL),(2067,'',10,2,NULL,NULL),(2068,'',10,2,NULL,NULL),(2069,'',10,2,NULL,NULL),(2070,'',10,2,NULL,NULL),(2071,'',10,2,NULL,NULL),(2072,'',10,2,NULL,NULL),(2073,'',10,2,NULL,NULL),(2074,'',10,2,NULL,NULL),(2075,'',10,2,NULL,NULL),(2076,'',10,2,NULL,NULL),(2077,'',10,2,NULL,NULL),(2078,'',10,2,NULL,NULL),(2079,'',10,2,NULL,NULL),(2080,'',10,2,NULL,NULL),(2081,'',10,2,NULL,NULL),(2082,'',10,2,NULL,NULL),(2083,'',10,2,NULL,NULL),(2084,'',10,2,NULL,NULL),(2085,'',10,2,NULL,NULL),(2086,'',10,2,NULL,NULL),(2087,'',10,2,NULL,NULL),(2088,'',10,2,NULL,NULL),(2089,'',10,2,NULL,NULL),(2090,'',10,2,NULL,NULL),(2091,'',10,2,NULL,NULL),(2092,'',10,2,NULL,NULL),(2093,'',10,2,NULL,NULL),(2094,'',10,2,NULL,NULL),(2095,'',10,2,NULL,NULL),(2096,'',10,2,NULL,NULL),(2097,'',10,2,NULL,NULL),(2098,'',10,2,NULL,NULL),(2099,'',10,2,NULL,NULL),(2100,'',10,2,NULL,NULL),(2101,'',10,2,NULL,NULL),(2102,'',10,2,NULL,NULL),(2103,'',10,2,NULL,NULL),(2104,'',10,2,NULL,NULL),(2105,'',10,2,NULL,NULL),(2106,'',10,2,NULL,NULL),(2107,'',10,2,NULL,NULL),(2108,'',10,2,NULL,NULL),(2109,'',10,2,NULL,NULL),(2110,'',10,2,NULL,NULL),(2111,'',10,2,NULL,NULL),(2112,'',10,2,NULL,NULL),(2113,'',10,2,NULL,NULL),(2114,'',10,2,NULL,NULL),(2115,'',10,2,NULL,NULL),(2116,'',10,2,NULL,NULL),(2117,'',10,2,NULL,NULL),(2118,'',10,2,NULL,NULL),(2119,'',10,2,NULL,NULL),(2120,'',10,2,NULL,NULL),(2121,'',10,2,NULL,NULL),(2122,'',10,2,NULL,NULL),(2123,'',10,2,NULL,NULL),(2124,'',10,2,NULL,NULL),(2125,'',10,2,NULL,NULL),(2126,'',10,2,NULL,NULL),(2127,'',10,2,NULL,NULL),(2128,'',10,2,NULL,NULL),(2129,'',10,2,NULL,NULL),(2130,'',10,2,NULL,NULL),(2131,'',10,2,NULL,NULL),(2132,'',10,2,NULL,NULL),(2133,'',10,2,NULL,NULL),(2134,'',10,2,NULL,NULL),(2135,'',10,2,NULL,NULL),(2136,'',10,2,NULL,NULL),(2137,'',10,2,NULL,NULL),(2138,'',10,2,NULL,NULL),(2139,'',10,2,NULL,NULL),(2140,'',10,2,NULL,NULL),(2141,'',10,2,NULL,NULL),(2142,'',10,2,NULL,NULL),(2143,'',10,2,NULL,NULL),(2144,'',10,2,NULL,NULL),(2145,'',10,2,NULL,NULL),(2146,'',10,2,NULL,NULL),(2147,'',10,2,NULL,NULL),(2148,'',10,2,NULL,NULL),(2149,'',10,2,NULL,NULL),(2150,'',10,2,NULL,NULL),(2151,'',10,2,NULL,NULL),(2152,'',10,2,NULL,NULL),(2153,'',10,2,NULL,NULL),(2154,'',10,2,NULL,NULL),(2155,'',10,2,NULL,NULL),(2156,'',10,2,NULL,NULL),(2157,'',10,2,NULL,NULL),(2158,'',10,2,NULL,NULL),(2159,'',10,2,NULL,NULL),(2160,'',10,2,NULL,NULL),(2161,'',10,2,NULL,NULL),(2162,'',10,2,NULL,NULL),(2163,'',10,2,NULL,NULL),(2164,'',10,2,NULL,NULL),(2165,'',10,2,NULL,NULL),(2166,'',10,2,NULL,NULL),(2167,'',10,2,NULL,NULL),(2168,'',10,2,NULL,NULL),(2169,'',10,2,NULL,NULL),(2170,'',10,2,NULL,NULL),(2171,'',10,2,NULL,NULL),(2172,'',10,2,NULL,NULL),(2173,'',10,2,NULL,NULL),(2174,'',10,2,NULL,NULL),(2175,'',10,2,NULL,NULL),(2176,'',10,2,NULL,NULL),(2177,'',10,2,NULL,NULL),(2178,'',10,2,NULL,NULL),(2179,'',10,2,NULL,NULL),(2180,'',10,2,NULL,NULL),(2181,'',10,2,NULL,NULL),(2182,'',10,2,NULL,NULL),(2183,'',10,2,NULL,NULL),(2184,'',10,2,NULL,NULL),(2185,'',10,2,NULL,NULL),(2186,'',10,2,NULL,NULL),(2187,'',10,2,NULL,NULL),(2188,'',10,2,NULL,NULL),(2189,'',10,2,NULL,NULL),(2190,'',10,2,NULL,NULL),(2191,'',10,2,NULL,NULL),(2192,'',10,2,NULL,NULL),(2193,'',10,2,NULL,NULL),(2194,'',10,2,NULL,NULL),(2195,'',10,2,NULL,NULL),(2196,'',10,2,NULL,NULL),(2197,'',10,2,NULL,NULL),(2198,'',10,2,NULL,NULL),(2199,'',10,2,NULL,NULL),(2200,'',10,2,NULL,NULL),(2201,'',10,2,NULL,NULL),(2202,'',10,2,NULL,NULL),(2203,'',10,2,NULL,NULL),(2204,'',10,2,NULL,NULL),(2205,'',10,2,NULL,NULL),(2206,'',10,2,NULL,NULL),(2207,'',10,2,NULL,NULL),(2208,'',10,2,NULL,NULL),(2209,'',10,2,NULL,NULL),(2210,'',10,2,NULL,NULL),(2211,'',10,2,NULL,NULL),(2212,'',10,2,NULL,NULL),(2213,'',10,2,NULL,NULL),(2214,'',10,2,NULL,NULL),(2215,'',10,2,NULL,NULL),(2216,'',10,2,NULL,NULL),(2217,'',10,2,NULL,NULL),(2218,'',10,2,NULL,NULL),(2219,'',10,2,NULL,NULL),(2220,'',10,2,NULL,NULL),(2221,'',10,2,NULL,NULL),(2222,'',10,2,NULL,NULL),(2223,'',10,2,NULL,NULL),(2224,'',10,2,NULL,NULL),(2225,'',10,2,NULL,NULL),(2226,'',10,2,NULL,NULL),(2227,'',10,2,NULL,NULL),(2228,'',10,2,NULL,NULL),(2229,'',10,2,NULL,NULL),(2230,'',10,2,NULL,NULL),(2231,'',10,2,NULL,NULL),(2232,'',10,2,NULL,NULL),(2233,'',10,2,NULL,NULL),(2234,'',10,2,NULL,NULL),(2235,'',10,2,NULL,NULL),(2236,'',10,2,NULL,NULL),(2237,'',10,2,NULL,NULL),(2238,'',10,2,NULL,NULL),(2239,'',10,2,NULL,NULL),(2240,'',10,2,NULL,NULL),(2241,'',10,2,NULL,NULL),(2242,'',10,2,NULL,NULL),(2243,'',10,2,NULL,NULL),(2244,'',10,2,NULL,NULL),(2245,'',10,2,NULL,NULL),(2246,'',10,2,NULL,NULL),(2247,'',10,2,NULL,NULL),(2248,'',10,2,NULL,NULL),(2249,'',10,2,NULL,NULL),(2250,'',10,2,NULL,NULL),(2251,'',10,2,NULL,NULL),(2252,'',10,2,NULL,NULL),(2253,'',10,2,NULL,NULL),(2254,'',10,2,NULL,NULL),(2255,'',10,2,NULL,NULL),(2256,'',10,2,NULL,NULL),(2257,'',10,2,NULL,NULL),(2258,'',10,2,NULL,NULL),(2259,'',10,2,NULL,NULL),(2260,'',10,2,NULL,NULL),(2261,'',10,2,NULL,NULL),(2262,'',10,2,NULL,NULL),(2263,'',10,2,NULL,NULL),(2264,'',10,2,NULL,NULL),(2265,'',10,2,NULL,NULL),(2266,'',10,2,NULL,NULL),(2267,'',10,2,NULL,NULL),(2268,'',10,2,NULL,NULL),(2269,'',10,2,NULL,NULL),(2270,'',10,2,NULL,NULL),(2271,'',10,2,NULL,NULL),(2272,'',10,2,NULL,NULL),(2273,'',10,2,NULL,NULL),(2274,'',10,2,NULL,NULL),(2275,'',10,2,NULL,NULL),(2276,'',10,2,NULL,NULL),(2277,'',10,2,NULL,NULL),(2278,'',10,2,NULL,NULL),(2279,'',10,2,NULL,NULL),(2280,'',10,2,NULL,NULL),(2281,'',10,2,NULL,NULL),(2282,'',10,2,NULL,NULL),(2283,'',10,2,NULL,NULL),(2284,'',10,2,NULL,NULL),(2285,'',10,2,NULL,NULL),(2286,'',10,2,NULL,NULL),(2287,'',10,2,NULL,NULL),(2288,'',10,2,NULL,NULL),(2289,'',10,2,NULL,NULL),(2290,'',10,2,NULL,NULL),(2291,'',10,2,NULL,NULL),(2292,'',10,2,NULL,NULL),(2293,'',10,2,NULL,NULL),(2294,'',10,2,NULL,NULL),(2295,'',10,2,NULL,NULL),(2296,'',10,2,NULL,NULL),(2297,'',10,2,NULL,NULL),(2298,'',10,2,NULL,NULL),(2299,'',10,2,NULL,NULL),(2300,'',10,2,NULL,NULL),(2301,'',10,2,NULL,NULL),(2302,'',10,2,NULL,NULL),(2303,'',10,2,NULL,NULL),(2304,'',10,2,NULL,NULL),(2305,'',10,2,NULL,NULL),(2306,'',10,2,NULL,NULL),(2307,'',10,2,NULL,NULL),(2308,'',10,2,NULL,NULL),(2309,'',10,2,NULL,NULL),(2310,'',10,2,NULL,NULL),(2311,'',10,2,NULL,NULL),(2312,'',10,2,NULL,NULL),(2313,'',10,2,NULL,NULL),(2314,'',10,2,NULL,NULL),(2315,'',10,2,NULL,NULL),(2316,'',10,2,NULL,NULL),(2317,'',10,2,NULL,NULL),(2318,'',10,2,NULL,NULL),(2319,'',10,2,NULL,NULL),(2320,'',10,2,NULL,NULL),(2321,'',10,2,NULL,NULL),(2322,'',10,2,NULL,NULL),(2323,'',10,2,NULL,NULL),(2324,'',10,2,NULL,NULL),(2325,'',10,2,NULL,NULL),(2326,'',10,2,NULL,NULL),(2327,'',10,2,NULL,NULL),(2328,'',10,2,NULL,NULL),(2329,'',10,2,NULL,NULL),(2330,'',10,2,NULL,NULL),(2331,'',10,2,NULL,NULL),(2332,'',10,2,NULL,NULL),(2333,'',10,2,NULL,NULL),(2334,'',10,2,NULL,NULL),(2335,'',10,2,NULL,NULL),(2336,'',10,2,NULL,NULL),(2337,'',10,2,NULL,NULL),(2338,'',10,2,NULL,NULL),(2339,'',10,2,NULL,NULL),(2340,'',10,2,NULL,NULL),(2341,'',10,2,NULL,NULL),(2342,'',10,2,NULL,NULL),(2343,'',10,2,NULL,NULL),(2344,'',10,2,NULL,NULL),(2345,'',10,2,NULL,NULL),(2346,'',10,2,NULL,NULL),(2347,'',10,2,NULL,NULL),(2348,'',10,2,NULL,NULL),(2349,'',10,2,NULL,NULL),(2350,'',10,2,NULL,NULL),(2351,'',10,2,NULL,NULL),(2352,'',10,2,NULL,NULL),(2353,'',10,2,NULL,NULL),(2354,'',10,2,NULL,NULL),(2355,'',10,2,NULL,NULL),(2356,'',10,2,NULL,NULL),(2357,'',10,2,NULL,NULL),(2358,'',10,2,NULL,NULL),(2359,'',10,2,NULL,NULL),(2360,'',10,2,NULL,NULL),(2361,'',10,2,NULL,NULL),(2362,'',10,2,NULL,NULL),(2363,'',10,2,NULL,NULL),(2364,'',10,2,NULL,NULL),(2365,'',10,2,NULL,NULL),(2366,'',10,2,NULL,NULL),(2367,'',10,2,NULL,NULL),(2368,'',10,2,NULL,NULL),(2369,'',10,2,NULL,NULL),(2370,'',10,2,NULL,NULL),(2371,'',10,2,NULL,NULL),(2372,'',10,2,NULL,NULL),(2373,'',10,2,NULL,NULL),(2374,'',10,2,NULL,NULL),(2375,'',10,2,NULL,NULL),(2376,'',10,2,NULL,NULL),(2377,'',10,2,NULL,NULL),(2378,'',10,2,NULL,NULL),(2379,'',10,2,NULL,NULL),(2380,'',10,2,NULL,NULL),(2381,'',10,2,NULL,NULL),(2382,'',10,2,NULL,NULL),(2383,'',10,2,NULL,NULL),(2384,'',10,2,NULL,NULL),(2385,'',10,2,NULL,NULL),(2386,'',10,2,NULL,NULL),(2387,'',10,2,NULL,NULL),(2388,'',10,2,NULL,NULL),(2389,'',10,2,NULL,NULL),(2390,'',10,2,NULL,NULL),(2391,'',10,2,NULL,NULL),(2392,'',10,2,NULL,NULL),(2393,'',10,2,NULL,NULL),(2394,'',10,2,NULL,NULL),(2395,'',10,2,NULL,NULL),(2396,'',10,2,NULL,NULL),(2397,'',10,2,NULL,NULL),(2398,'',10,2,NULL,NULL),(2399,'',10,2,NULL,NULL),(2400,'',10,2,NULL,NULL),(2401,'',10,2,NULL,NULL),(2402,'',10,2,NULL,NULL),(2403,'',10,2,NULL,NULL),(2404,'',10,2,NULL,NULL),(2405,'',10,2,NULL,NULL),(2406,'',10,2,NULL,NULL),(2407,'',10,2,NULL,NULL),(2408,'',10,2,NULL,NULL),(2409,'',10,2,NULL,NULL),(2410,'',10,2,NULL,NULL),(2411,'',10,2,NULL,NULL),(2412,'',10,2,NULL,NULL),(2413,'',10,2,NULL,NULL),(2414,'',10,2,NULL,NULL),(2415,'',10,2,NULL,NULL),(2416,'',10,2,NULL,NULL),(2417,'',10,2,NULL,NULL),(2418,'',10,2,NULL,NULL),(2419,'',10,2,NULL,NULL),(2420,'',10,2,NULL,NULL),(2421,'',10,2,NULL,NULL),(2422,'',10,2,NULL,NULL),(2423,'',10,2,NULL,NULL),(2424,'',10,2,NULL,NULL),(2425,'',10,2,NULL,NULL),(2426,'',10,2,NULL,NULL),(2427,'',10,2,NULL,NULL),(2428,'',10,2,NULL,NULL),(2429,'',10,2,NULL,NULL),(2430,'',10,2,NULL,NULL),(2431,'',10,2,NULL,NULL),(2432,'',10,2,NULL,NULL),(2433,'',10,2,NULL,NULL),(2434,'',10,2,NULL,NULL),(2435,'',10,2,NULL,NULL),(2436,'',10,2,NULL,NULL),(2437,'',10,2,NULL,NULL),(2438,'',10,2,NULL,NULL),(2439,'',10,2,NULL,NULL),(2440,'',10,2,NULL,NULL),(2441,'',10,2,NULL,NULL),(2442,'',10,2,NULL,NULL),(2443,'',10,2,NULL,NULL),(2444,'',10,2,NULL,NULL),(2445,'',10,2,NULL,NULL),(2446,'',10,2,NULL,NULL),(2447,'',10,2,NULL,NULL),(2448,'',10,2,NULL,NULL),(2449,'',10,2,NULL,NULL),(2450,'',10,2,NULL,NULL),(2451,'',10,2,NULL,NULL),(2452,'',10,2,NULL,NULL),(2453,'',10,2,NULL,NULL),(2454,'',10,2,NULL,NULL),(2455,'',10,2,NULL,NULL),(2456,'',10,2,NULL,NULL),(2457,'',10,2,NULL,NULL),(2458,'',10,2,NULL,NULL),(2459,'',10,2,NULL,NULL),(2460,'',10,2,NULL,NULL),(2461,'',10,2,NULL,NULL),(2462,'',10,2,NULL,NULL),(2463,'',10,2,NULL,NULL),(2464,'',10,2,NULL,NULL),(2465,'',10,2,NULL,NULL),(2466,'',10,2,NULL,NULL),(2467,'',10,2,NULL,NULL),(2468,'',10,2,NULL,NULL),(2469,'',10,2,NULL,NULL),(2470,'',10,2,NULL,NULL),(2471,'',10,2,NULL,NULL),(2472,'',10,2,NULL,NULL),(2473,'',10,2,NULL,NULL),(2474,'',10,2,NULL,NULL),(2475,'',10,2,NULL,NULL),(2476,'',10,2,NULL,NULL),(2477,'',10,2,NULL,NULL),(2478,'',10,2,NULL,NULL),(2479,'',10,2,NULL,NULL),(2480,'',10,2,NULL,NULL),(2481,'',10,2,NULL,NULL),(2482,'',10,2,NULL,NULL),(2483,'',10,2,NULL,NULL),(2484,'',10,2,NULL,NULL),(2485,'',10,2,NULL,NULL),(2486,'',10,2,NULL,NULL),(2487,'',10,2,NULL,NULL),(2488,'',10,2,NULL,NULL),(2489,'',10,2,NULL,NULL),(2490,'',10,2,NULL,NULL),(2491,'',10,2,NULL,NULL),(2492,'',10,2,NULL,NULL),(2493,'',10,2,NULL,NULL),(2494,'',10,2,NULL,NULL),(2495,'',10,2,NULL,NULL),(2496,'',10,2,NULL,NULL),(2497,'',10,2,NULL,NULL),(2498,'',10,2,NULL,NULL),(2499,'',10,2,NULL,NULL),(2500,'',10,2,NULL,NULL),(2501,'',10,2,NULL,NULL),(2502,'',10,2,NULL,NULL),(2503,'',10,2,NULL,NULL),(2504,'',10,2,NULL,NULL),(2505,'',10,2,NULL,NULL),(2506,'',10,2,NULL,NULL),(2507,'',10,2,NULL,NULL),(2508,'',10,2,NULL,NULL),(2509,'',10,2,NULL,NULL),(2510,'',10,2,NULL,NULL),(2511,'',10,2,NULL,NULL),(2512,'',10,2,NULL,NULL),(2513,'',10,2,NULL,NULL),(2514,'',10,2,NULL,NULL),(2515,'',10,2,NULL,NULL),(2516,'',10,2,NULL,NULL),(2517,'',10,2,NULL,NULL),(2518,'',10,2,NULL,NULL),(2519,'',10,2,NULL,NULL),(2520,'',10,2,NULL,NULL),(2521,'',10,2,NULL,NULL),(2522,'',10,2,NULL,NULL),(2523,'',10,2,NULL,NULL),(2524,'',10,2,NULL,NULL),(2525,'',10,2,NULL,NULL),(2526,'',10,2,NULL,NULL),(2527,'',10,2,NULL,NULL),(2528,'',10,2,NULL,NULL),(2529,'',10,2,NULL,NULL),(2530,'',10,2,NULL,NULL),(2531,'',10,2,NULL,NULL),(2532,'',10,2,NULL,NULL),(2533,'',10,2,NULL,NULL),(2534,'',10,2,NULL,NULL),(2535,'',10,2,NULL,NULL),(2536,'',10,2,NULL,NULL),(2537,'',10,2,NULL,NULL),(2538,'',10,2,NULL,NULL),(2539,'',10,2,NULL,NULL),(2540,'',10,2,NULL,NULL),(2541,'',10,2,NULL,NULL),(2542,'',10,2,NULL,NULL),(2543,'',10,2,NULL,NULL),(2544,'',10,2,NULL,NULL),(2545,'',10,2,NULL,NULL),(2546,'',10,2,NULL,NULL),(2547,'',10,2,NULL,NULL),(2548,'',10,2,NULL,NULL),(2549,'',10,2,NULL,NULL),(2550,'',10,2,NULL,NULL),(2551,'',10,2,NULL,NULL),(2552,'',10,2,NULL,NULL),(2553,'',10,2,NULL,NULL),(2554,'',10,2,NULL,NULL),(2555,'',10,2,NULL,NULL),(2556,'',10,2,NULL,NULL),(2557,'',10,2,NULL,NULL),(2558,'',10,2,NULL,NULL),(2559,'',10,2,NULL,NULL),(2560,'',10,2,NULL,NULL),(2561,'',10,2,NULL,NULL),(2562,'',10,2,NULL,NULL),(2563,'',10,2,NULL,NULL),(2564,'',10,2,NULL,NULL),(2565,'',10,2,NULL,NULL),(2566,'',10,2,NULL,NULL),(2567,'',10,2,NULL,NULL),(2568,'',10,2,NULL,NULL),(2569,'',10,2,NULL,NULL),(2570,'',10,2,NULL,NULL),(2571,'',10,2,NULL,NULL),(2572,'',10,2,NULL,NULL),(2573,'',10,2,NULL,NULL),(2574,'',10,2,NULL,NULL),(2575,'',10,2,NULL,NULL),(2576,'',10,2,NULL,NULL),(2577,'',10,2,NULL,NULL),(2578,'',10,2,NULL,NULL),(2579,'',10,2,NULL,NULL),(2580,'',10,2,NULL,NULL),(2581,'',10,2,NULL,NULL),(2582,'',10,2,NULL,NULL),(2583,'',10,2,NULL,NULL),(2584,'',10,2,NULL,NULL),(2585,'',10,2,NULL,NULL),(2586,'',10,2,NULL,NULL),(2587,'',10,2,NULL,NULL),(2588,'',10,2,NULL,NULL),(2589,'',10,2,NULL,NULL),(2590,'',10,2,NULL,NULL),(2591,'',10,2,NULL,NULL),(2592,'',10,2,NULL,NULL),(2593,'',10,2,NULL,NULL),(2594,'',10,2,NULL,NULL),(2595,'',10,2,NULL,NULL),(2596,'',10,2,NULL,NULL),(2597,'',10,2,NULL,NULL),(2598,'',10,2,NULL,NULL),(2599,'',10,2,NULL,NULL),(2600,'',10,2,NULL,NULL),(2601,'',10,2,NULL,NULL),(2602,'',10,2,NULL,NULL),(2603,'',10,2,NULL,NULL),(2604,'',10,2,NULL,NULL),(2605,'',10,2,NULL,NULL),(2606,'',10,2,NULL,NULL),(2607,'',10,2,NULL,NULL),(2608,'',10,2,NULL,NULL),(2609,'',10,2,NULL,NULL),(2610,'',10,2,NULL,NULL),(2611,'',10,2,NULL,NULL),(2612,'',10,2,NULL,NULL),(2613,'',10,2,NULL,NULL),(2614,'',10,2,NULL,NULL),(2615,'',10,2,NULL,NULL),(2616,'',10,2,NULL,NULL),(2617,'',10,2,NULL,NULL),(2618,'',10,2,NULL,NULL),(2619,'',10,2,NULL,NULL),(2620,'',10,2,NULL,NULL),(2621,'',10,2,NULL,NULL),(2622,'',10,2,NULL,NULL),(2623,'',10,2,NULL,NULL),(2624,'',10,2,NULL,NULL),(2625,'',10,2,NULL,NULL),(2626,'',10,2,NULL,NULL),(2627,'',10,2,NULL,NULL),(2628,'',10,2,NULL,NULL),(2629,'',10,2,NULL,NULL),(2630,'',10,2,NULL,NULL),(2631,'',10,2,NULL,NULL),(2632,'',10,2,NULL,NULL),(2633,'',10,2,NULL,NULL),(2634,'',10,2,NULL,NULL),(2635,'',10,2,NULL,NULL),(2636,'',10,2,NULL,NULL),(2637,'',10,2,NULL,NULL),(2638,'',10,2,NULL,NULL),(2639,'',10,2,NULL,NULL),(2640,'',10,2,NULL,NULL),(2641,'',10,2,NULL,NULL),(2642,'',10,2,NULL,NULL),(2643,'',10,2,NULL,NULL),(2644,'',10,2,NULL,NULL),(2645,'',10,2,NULL,NULL),(2646,'',10,2,NULL,NULL),(2647,'',10,2,NULL,NULL),(2648,'',10,2,NULL,NULL),(2649,'',10,2,NULL,NULL),(2650,'',10,2,NULL,NULL),(2651,'',10,2,NULL,NULL),(2652,'',10,2,NULL,NULL),(2653,'',10,2,NULL,NULL),(2654,'',10,2,NULL,NULL),(2655,'',10,2,NULL,NULL),(2656,'',10,2,NULL,NULL),(2657,'',10,2,NULL,NULL),(2658,'',10,2,NULL,NULL),(2659,'',10,2,NULL,NULL),(2660,'',10,2,NULL,NULL),(2661,'',10,2,NULL,NULL),(2662,'',10,2,NULL,NULL),(2663,'',10,2,NULL,NULL),(2664,'',10,2,NULL,NULL),(2665,'',10,2,NULL,NULL),(2666,'',10,2,NULL,NULL),(2667,'',10,2,NULL,NULL),(2668,'',10,2,NULL,NULL),(2669,'',10,2,NULL,NULL),(2670,'',10,2,NULL,NULL),(2671,'',10,2,NULL,NULL),(2672,'',10,2,NULL,NULL),(2673,'',10,2,NULL,NULL),(2674,'',10,2,NULL,NULL),(2675,'',10,2,NULL,NULL),(2676,'',10,2,NULL,NULL),(2677,'',10,2,NULL,NULL),(2678,'',10,2,NULL,NULL),(2679,'',10,2,NULL,NULL),(2680,'',10,2,NULL,NULL),(2681,'',10,2,NULL,NULL),(2682,'',10,2,NULL,NULL),(2683,'',10,2,NULL,NULL),(2684,'',10,2,NULL,NULL),(2685,'',10,2,NULL,NULL),(2686,'',10,2,NULL,NULL),(2687,'',10,2,NULL,NULL),(2688,'',10,2,NULL,NULL),(2689,'',10,2,NULL,NULL),(2690,'',10,2,NULL,NULL),(2691,'',10,2,NULL,NULL),(2692,'',10,2,NULL,NULL),(2693,'',10,2,NULL,NULL),(2694,'',10,2,NULL,NULL),(2695,'',10,2,NULL,NULL),(2696,'',10,2,NULL,NULL),(2697,'',10,2,NULL,NULL),(2698,'',10,2,NULL,NULL),(2699,'',10,2,NULL,NULL),(2700,'',10,2,NULL,NULL),(2701,'',10,2,NULL,NULL),(2702,'',10,2,NULL,NULL),(2703,'',10,2,NULL,NULL),(2704,'',10,2,NULL,NULL),(2705,'',10,2,NULL,NULL),(2706,'',10,2,NULL,NULL),(2707,'',10,2,NULL,NULL),(2708,'',10,2,NULL,NULL),(2709,'',10,2,NULL,NULL),(2710,'',10,2,NULL,NULL),(2711,'',10,2,NULL,NULL),(2712,'',10,2,NULL,NULL),(2713,'',10,2,NULL,NULL),(2714,'',10,2,NULL,NULL),(2715,'',10,2,NULL,NULL),(2716,'',10,2,NULL,NULL),(2717,'',10,2,NULL,NULL),(2718,'',10,2,NULL,NULL),(2719,'',10,2,NULL,NULL),(2720,'',10,2,NULL,NULL),(2721,'',10,2,NULL,NULL),(2722,'',10,2,NULL,NULL),(2723,'',10,2,NULL,NULL),(2724,'',10,2,NULL,NULL),(2725,'',10,2,NULL,NULL),(2726,'',10,2,NULL,NULL),(2727,'',10,2,NULL,NULL),(2728,'',10,2,NULL,NULL),(2729,'',10,2,NULL,NULL),(2730,'',10,2,NULL,NULL),(2731,'',10,2,NULL,NULL),(2732,'',10,2,NULL,NULL),(2733,'',10,2,NULL,NULL),(2734,'',10,2,NULL,NULL),(2735,'',10,2,NULL,NULL),(2736,'',10,2,NULL,NULL),(2737,'',10,2,NULL,NULL),(2738,'',10,2,NULL,NULL),(2739,'',10,2,NULL,NULL),(2740,'',10,2,NULL,NULL),(2741,'',10,2,NULL,NULL),(2742,'',10,2,NULL,NULL),(2743,'',10,2,NULL,NULL),(2744,'',10,2,NULL,NULL),(2745,'',10,2,NULL,NULL),(2746,'',10,2,NULL,NULL),(2747,'',10,2,NULL,NULL),(2748,'',10,2,NULL,NULL),(2749,'',10,2,NULL,NULL),(2750,'',10,2,NULL,NULL),(2751,'',10,2,NULL,NULL),(2752,'',10,2,NULL,NULL),(2753,'',10,2,NULL,NULL),(2754,'',10,2,NULL,NULL),(2755,'',10,2,NULL,NULL),(2756,'',10,2,NULL,NULL),(2757,'',10,2,NULL,NULL),(2758,'',10,2,NULL,NULL),(2759,'',10,2,NULL,NULL),(2760,'',10,2,NULL,NULL),(2761,'',10,2,NULL,NULL),(2762,'',10,2,NULL,NULL),(2763,'',10,2,NULL,NULL),(2764,'',10,2,NULL,NULL),(2765,'',10,2,NULL,NULL),(2766,'',10,2,NULL,NULL),(2767,'',10,2,NULL,NULL),(2768,'',10,2,NULL,NULL),(2769,'',10,2,NULL,NULL),(2770,'',10,2,NULL,NULL),(2771,'',10,2,NULL,NULL),(2772,'',10,2,NULL,NULL),(2773,'',10,2,NULL,NULL),(2774,'',10,2,NULL,NULL),(2775,'',10,2,NULL,NULL),(2776,'',10,2,NULL,NULL),(2777,'',10,2,NULL,NULL),(2778,'',10,2,NULL,NULL),(2779,'',10,2,NULL,NULL),(2780,'',10,2,NULL,NULL),(2781,'',10,2,NULL,NULL),(2782,'',10,2,NULL,NULL),(2783,'',10,2,NULL,NULL),(2784,'',10,2,NULL,NULL),(2785,'',10,2,NULL,NULL),(2786,'',10,2,NULL,NULL),(2787,'',10,2,NULL,NULL),(2788,'',10,2,NULL,NULL),(2789,'',10,2,NULL,NULL),(2790,'',10,2,NULL,NULL),(2791,'',10,2,NULL,NULL),(2792,'',10,2,NULL,NULL),(2793,'',10,2,NULL,NULL),(2794,'',10,2,NULL,NULL),(2795,'',10,2,NULL,NULL),(2796,'',10,2,NULL,NULL),(2797,'',10,2,NULL,NULL),(2798,'',10,2,NULL,NULL),(2799,'',10,2,NULL,NULL),(2800,'',10,2,NULL,NULL),(2801,'',10,2,NULL,NULL),(2802,'',10,2,NULL,NULL),(2803,'',10,2,NULL,NULL),(2804,'',10,2,NULL,NULL),(2805,'',10,2,NULL,NULL),(2806,'',10,2,NULL,NULL),(2807,'',10,2,NULL,NULL),(2808,'',10,2,NULL,NULL),(2809,'',10,2,NULL,NULL),(2810,'',10,2,NULL,NULL),(2811,'',10,2,NULL,NULL),(2812,'',10,2,NULL,NULL),(2813,'',10,2,NULL,NULL),(2814,'',10,2,NULL,NULL),(2815,'',10,2,NULL,NULL),(2816,'',10,2,NULL,NULL),(2817,'',10,2,NULL,NULL),(2818,'',10,2,NULL,NULL),(2819,'',10,2,NULL,NULL),(2820,'',10,2,NULL,NULL),(2821,'',10,2,NULL,NULL),(2822,'',10,2,NULL,NULL),(2823,'',10,2,NULL,NULL),(2824,'',10,2,NULL,NULL),(2825,'',10,2,NULL,NULL),(2826,'',10,2,NULL,NULL),(2827,'',10,2,NULL,NULL),(2828,'',10,2,NULL,NULL),(2829,'',10,2,NULL,NULL),(2830,'',10,2,NULL,NULL),(2831,'',10,2,NULL,NULL),(2832,'',10,2,NULL,NULL),(2833,'',10,2,NULL,NULL),(2834,'',10,2,NULL,NULL),(2835,'',10,2,NULL,NULL),(2836,'',10,2,NULL,NULL),(2837,'',10,2,NULL,NULL),(2838,'',10,2,NULL,NULL),(2839,'',10,2,NULL,NULL),(2840,'',10,2,NULL,NULL),(2841,'',10,2,NULL,NULL),(2842,'',10,2,NULL,NULL),(2843,'',10,2,NULL,NULL),(2844,'',10,2,NULL,NULL),(2845,'',10,2,NULL,NULL),(2846,'',10,2,NULL,NULL),(2847,'',10,2,NULL,NULL),(2848,'',10,2,NULL,NULL),(2849,'',10,2,NULL,NULL),(2850,'',10,2,NULL,NULL),(2851,'',10,2,NULL,NULL),(2852,'',10,2,NULL,NULL),(2853,'',10,2,NULL,NULL),(2854,'',10,2,NULL,NULL),(2855,'',10,2,NULL,NULL),(2856,'',10,2,NULL,NULL),(2857,'',10,2,NULL,NULL),(2858,'',10,2,NULL,NULL),(2859,'',10,2,NULL,NULL),(2860,'',10,2,NULL,NULL),(2861,'',10,2,NULL,NULL),(2862,'',10,2,NULL,NULL),(2863,'',10,2,NULL,NULL),(2864,'',10,2,NULL,NULL),(2865,'',10,2,NULL,NULL),(2866,'',10,2,NULL,NULL),(2867,'',10,2,NULL,NULL),(2868,'',10,2,NULL,NULL),(2869,'',10,2,NULL,NULL),(2870,'',10,2,NULL,NULL),(2871,'',10,2,NULL,NULL),(2872,'',10,2,NULL,NULL),(2873,'',10,2,NULL,NULL),(2874,'',10,2,NULL,NULL),(2875,'',10,2,NULL,NULL),(2876,'',10,2,NULL,NULL),(2877,'',10,2,NULL,NULL),(2878,'',10,2,NULL,NULL),(2879,'',10,2,NULL,NULL),(2880,'',10,2,NULL,NULL),(2881,'',10,2,NULL,NULL),(2882,'',10,2,NULL,NULL),(2883,'',10,2,NULL,NULL),(2884,'',10,2,NULL,NULL),(2885,'',10,2,NULL,NULL),(2886,'',10,2,NULL,NULL),(2887,'',10,2,NULL,NULL),(2888,'',10,2,NULL,NULL),(2889,'',10,2,NULL,NULL),(2890,'',10,2,NULL,NULL),(2891,'',10,2,NULL,NULL),(2892,'',10,2,NULL,NULL),(2893,'',10,2,NULL,NULL),(2894,'',10,2,NULL,NULL),(2895,'',10,2,NULL,NULL),(2896,'',10,2,NULL,NULL),(2897,'',10,2,NULL,NULL),(2898,'',10,2,NULL,NULL),(2899,'',10,2,NULL,NULL),(2900,'',10,2,NULL,NULL),(2901,'',10,2,NULL,NULL),(2902,'',10,2,NULL,NULL),(2903,'',10,2,NULL,NULL),(2904,'',10,2,NULL,NULL),(2905,'',10,2,NULL,NULL),(2906,'',10,2,NULL,NULL),(2907,'',10,2,NULL,NULL),(2908,'',10,2,NULL,NULL),(2909,'',10,2,NULL,NULL),(2910,'',10,2,NULL,NULL),(2911,'',10,2,NULL,NULL),(2912,'',10,2,NULL,NULL),(2913,'',10,2,NULL,NULL),(2914,'',10,2,NULL,NULL),(2915,'',10,2,NULL,NULL),(2916,'',10,2,NULL,NULL),(2917,'',10,2,NULL,NULL),(2918,'',10,2,NULL,NULL),(2919,'',10,2,NULL,NULL),(2920,'',10,2,NULL,NULL),(2921,'',10,2,NULL,NULL),(2922,'',10,2,NULL,NULL),(2923,'',10,2,NULL,NULL),(2924,'',10,2,NULL,NULL),(2925,'',10,2,NULL,NULL),(2926,'',10,2,NULL,NULL),(2927,'',10,2,NULL,NULL),(2928,'',10,2,NULL,NULL),(2929,'',10,2,NULL,NULL),(2930,'',10,2,NULL,NULL),(2931,'',10,2,NULL,NULL),(2932,'',10,2,NULL,NULL),(2933,'',10,2,NULL,NULL),(2934,'',10,2,NULL,NULL),(2935,'',10,2,NULL,NULL),(2936,'',10,2,NULL,NULL),(2937,'',10,2,NULL,NULL),(2938,'',10,2,NULL,NULL),(2939,'',10,2,NULL,NULL),(2940,'',10,2,NULL,NULL),(2941,'',10,2,NULL,NULL),(2942,'',10,2,NULL,NULL),(2943,'',10,2,NULL,NULL),(2944,'',10,2,NULL,NULL),(2945,'',10,2,NULL,NULL),(2946,'',10,2,NULL,NULL),(2947,'',10,2,NULL,NULL),(2948,'',10,2,NULL,NULL),(2949,'',10,2,NULL,NULL),(2950,'',10,2,NULL,NULL),(2951,'',10,2,NULL,NULL),(2952,'',10,2,NULL,NULL),(2953,'',10,2,NULL,NULL),(2954,'',10,2,NULL,NULL),(2955,'',10,2,NULL,NULL),(2956,'',10,2,NULL,NULL),(2957,'',10,2,NULL,NULL),(2958,'',10,2,NULL,NULL),(2959,'',10,2,NULL,NULL),(2960,'',10,2,NULL,NULL),(2961,'',10,2,NULL,NULL),(2962,'',10,2,NULL,NULL),(2963,'',10,2,NULL,NULL),(2964,'',10,2,NULL,NULL),(2965,'',10,2,NULL,NULL),(2966,'',10,2,NULL,NULL),(2967,'',10,2,NULL,NULL),(2968,'',10,2,NULL,NULL),(2969,'',10,2,NULL,NULL),(2970,'',10,2,NULL,NULL),(2971,'',10,2,NULL,NULL),(2972,'',10,2,NULL,NULL),(2973,'',10,2,NULL,NULL),(2974,'',10,2,NULL,NULL),(2975,'',10,2,NULL,NULL),(2976,'',10,2,NULL,NULL),(2977,'',10,2,NULL,NULL),(2978,'',10,2,NULL,NULL),(2979,'',10,2,NULL,NULL),(2980,'',10,2,NULL,NULL),(2981,'',10,2,NULL,NULL),(2982,'',10,2,NULL,NULL),(2983,'',10,2,NULL,NULL),(2984,'',10,2,NULL,NULL),(2985,'',10,2,NULL,NULL),(2986,'',10,2,NULL,NULL),(2987,'',10,2,NULL,NULL),(2988,'',10,2,NULL,NULL),(2989,'',10,2,NULL,NULL),(2990,'',10,2,NULL,NULL),(2991,'',10,2,NULL,NULL),(2992,'',10,2,NULL,NULL),(2993,'',10,2,NULL,NULL),(2994,'',10,2,NULL,NULL),(2995,'',10,2,NULL,NULL),(2996,'',10,2,NULL,NULL),(2997,'',10,2,NULL,NULL),(2998,'',10,2,NULL,NULL),(2999,'',10,2,NULL,NULL),(3000,'',10,2,NULL,NULL),(3001,'',10,2,NULL,NULL),(3002,'',10,2,NULL,NULL),(3003,'',10,1,5,'2016-03-16 11:39:46'),(3004,'',10,1,13,'2016-03-16 11:42:02'),(3005,'',10,1,14,'2016-03-16 11:42:04'),(3006,'',10,1,15,'2016-03-16 11:42:05'),(3007,'',10,1,16,'2016-03-16 11:42:06'),(3008,'',10,1,17,'2016-03-16 11:42:07'),(3009,'',10,1,18,'2016-03-16 11:42:08'),(3010,'',10,1,19,'2016-03-16 11:42:10'),(3011,'',10,1,20,'2016-03-16 11:42:11'),(3012,'',10,1,21,'2016-03-16 11:42:12'),(3013,'',10,1,22,'2016-03-16 11:42:13'),(3014,'',10,1,23,'2016-03-16 11:42:15'),(3015,'',10,1,24,'2016-03-16 11:42:16'),(3016,'',10,1,25,'2016-03-16 11:42:17'),(3017,'',10,1,26,'2016-03-16 11:42:18'),(3018,'',10,1,27,'2016-03-16 11:42:19'),(3019,'',10,1,28,'2016-03-16 11:42:20'),(3020,'',10,1,29,'2016-03-16 11:42:21'),(3021,'',10,1,30,'2016-03-16 11:42:23'),(3022,'',10,1,31,'2016-03-16 11:42:24'),(3023,'',10,1,32,'2016-03-16 11:42:25'),(3024,'',10,1,33,'2016-03-16 11:42:26'),(3025,'',10,1,34,'2016-03-16 11:42:27'),(3026,'',10,1,35,'2016-03-16 11:42:28'),(3027,'',10,1,36,'2016-03-16 11:42:29'),(3028,'',10,1,37,'2016-03-16 11:42:31'),(3029,'',10,1,38,'2016-03-16 11:42:32'),(3030,'',10,1,39,'2016-03-16 11:42:33'),(3031,'',10,1,40,'2016-03-16 11:42:34'),(3032,'',10,1,41,'2016-03-16 11:42:35'),(3033,'',10,1,42,'2016-03-16 11:42:36'),(3034,'',10,1,43,'2016-03-16 11:42:37'),(3035,'',10,1,44,'2016-03-16 11:42:38'),(3036,'',10,1,45,'2016-03-16 11:42:39'),(3037,'',10,1,46,'2016-03-16 11:42:40'),(3038,'',10,1,47,'2016-03-16 11:42:41'),(3039,'',10,1,48,'2016-03-16 11:42:43'),(3040,'',10,1,49,'2016-03-16 11:42:44'),(3041,'',10,1,50,'2016-03-16 11:42:45'),(3042,'',10,1,51,'2016-03-16 11:42:46'),(3043,'',10,1,52,'2016-03-16 11:42:47'),(3044,'',10,1,53,'2016-03-16 11:42:48'),(3045,'',10,1,54,'2016-03-16 11:42:49'),(3046,'',10,1,55,'2016-03-16 11:42:50'),(3047,'',10,1,56,'2016-03-16 11:42:51'),(3048,'',10,1,57,'2016-03-16 11:42:52'),(3049,'',10,1,58,'2016-03-16 11:42:53'),(3050,'',10,1,59,'2016-03-16 11:42:54'),(3051,'',10,1,60,'2016-03-16 11:42:55'),(3052,'',10,1,61,'2016-03-16 11:42:56'),(3053,'',10,1,62,'2016-03-16 11:42:57'),(3054,'',10,1,63,'2016-03-16 11:42:58'),(3055,'',10,1,64,'2016-03-16 11:43:00'),(3056,'',10,1,65,'2016-03-16 11:43:01'),(3057,'',10,1,66,'2016-03-16 11:43:02'),(3058,'',10,1,67,'2016-03-16 11:43:03'),(3059,'',10,1,68,'2016-03-16 11:43:04'),(3060,'',10,1,69,'2016-03-16 11:43:05'),(3061,'',10,1,70,'2016-03-16 11:43:06'),(3062,'',10,1,71,'2016-03-16 11:43:07'),(3063,'',10,1,72,'2016-03-16 11:43:09'),(3064,'',10,1,73,'2016-03-16 11:43:10'),(3065,'',10,1,74,'2016-03-16 11:43:11'),(3066,'',10,1,75,'2016-03-16 11:43:12'),(3067,'',10,1,76,'2016-03-16 11:43:13'),(3068,'',10,1,77,'2016-03-16 11:43:14'),(3069,'',10,1,78,'2016-03-16 11:43:15'),(3070,'',10,1,79,'2016-03-16 11:43:16'),(3071,'',10,1,80,'2016-03-16 11:43:17'),(3072,'',10,1,81,'2016-03-16 11:43:19'),(3073,'',10,1,82,'2016-03-16 11:43:20'),(3074,'',10,1,83,'2016-03-16 11:43:21'),(3075,'',10,1,84,'2016-03-16 11:43:22'),(3076,'',10,1,85,'2016-03-16 11:43:23'),(3077,'',10,1,86,'2016-03-16 11:43:24'),(3078,'',10,1,87,'2016-03-16 11:43:25'),(3079,'',10,1,88,'2016-03-16 11:43:26'),(3080,'',10,1,89,'2016-03-16 11:43:27'),(3081,'',10,1,90,'2016-03-16 11:43:29'),(3082,'',10,1,91,'2016-03-16 11:43:30'),(3083,'',10,1,92,'2016-03-16 11:43:31'),(3084,'',10,1,93,'2016-03-16 11:43:32'),(3085,'',10,1,94,'2016-03-16 11:43:33'),(3086,'',10,1,95,'2016-03-16 11:43:34'),(3087,'',10,1,96,'2016-03-16 11:43:36'),(3088,'',10,1,97,'2016-03-16 11:43:37'),(3089,'',10,1,98,'2016-03-16 11:43:38'),(3090,'',10,1,99,'2016-03-16 11:43:39'),(3091,'',10,1,100,'2016-03-16 11:43:40'),(3092,'',10,1,101,'2016-03-16 11:43:41'),(3093,'',10,1,102,'2016-03-16 11:43:42'),(3094,'',10,1,103,'2016-03-16 11:43:43'),(3095,'',10,1,104,'2016-03-16 11:43:45'),(3096,'',10,1,105,'2016-03-16 11:43:46'),(3097,'',10,1,106,'2016-03-16 11:43:47'),(3098,'',10,1,107,'2016-03-16 11:43:48'),(3099,'',10,1,108,'2016-03-16 11:43:49'),(3100,'',10,1,109,'2016-03-16 11:43:50'),(3101,'',10,1,110,'2016-03-16 11:43:51'),(3102,'',10,1,111,'2016-03-16 11:43:52'),(3103,'',10,1,112,'2016-03-16 11:43:53'),(3104,'',10,1,113,'2016-03-16 11:43:55'),(3105,'',10,1,114,'2016-03-16 11:43:56'),(3106,'',10,1,115,'2016-03-16 11:43:56'),(3107,'',10,1,116,'2016-03-16 11:43:58'),(3108,'',10,1,117,'2016-03-16 11:43:59'),(3109,'',10,1,118,'2016-03-16 11:44:00'),(3110,'',10,1,119,'2016-03-16 11:44:01'),(3111,'',10,1,120,'2016-03-16 11:44:02'),(3112,'',10,1,121,'2016-03-16 11:44:03'),(3113,'',10,1,122,'2016-03-16 11:44:04'),(3114,'',10,1,182,'2016-07-07 11:22:59'),(3115,'',10,1,206,'2016-07-07 11:22:59'),(3116,'',10,1,213,'2016-07-07 11:22:59'),(3117,'',10,1,201,'2016-07-07 11:22:59'),(3118,'',10,1,139,'2016-07-07 11:22:59'),(3119,'',10,1,143,'2016-07-07 11:22:59'),(3120,'',10,1,160,'2016-07-07 11:22:59'),(3121,'',10,1,NULL,NULL),(3122,'',10,1,NULL,NULL),(3123,'',10,1,NULL,NULL),(3124,'',10,1,NULL,NULL),(3125,'',10,1,NULL,NULL),(3126,'',10,1,NULL,NULL),(3127,'',10,1,NULL,NULL),(3128,'',10,1,NULL,NULL),(3129,'',10,1,NULL,NULL),(3130,'',10,1,NULL,NULL),(3131,'',10,1,NULL,NULL),(3132,'',10,1,NULL,NULL),(3133,'',10,1,NULL,NULL),(3134,'',10,1,NULL,NULL),(3135,'',10,1,NULL,NULL),(3136,'',10,1,NULL,NULL),(3137,'',10,1,NULL,NULL),(3138,'',10,1,NULL,NULL),(3139,'',10,1,NULL,NULL),(3140,'',10,1,NULL,NULL),(3141,'',10,1,NULL,NULL),(3142,'',10,1,NULL,NULL),(3143,'',10,1,NULL,NULL),(3144,'',10,1,NULL,NULL),(3145,'',10,1,NULL,NULL),(3146,'',10,1,NULL,NULL),(3147,'',10,1,NULL,NULL),(3148,'',10,1,NULL,NULL),(3149,'',10,1,NULL,NULL),(3150,'',10,1,NULL,NULL),(3151,'',10,1,NULL,NULL),(3152,'',10,1,NULL,NULL),(3153,'',10,1,NULL,NULL),(3154,'',10,1,NULL,NULL),(3155,'',10,1,NULL,NULL),(3156,'',10,1,NULL,NULL),(3157,'',10,1,NULL,NULL),(3158,'',10,1,NULL,NULL),(3159,'',10,1,NULL,NULL),(3160,'',10,1,NULL,NULL),(3161,'',10,1,NULL,NULL),(3162,'',10,1,NULL,NULL),(3163,'',10,1,NULL,NULL),(3164,'',10,1,NULL,NULL),(3165,'',10,1,NULL,NULL),(3166,'',10,1,NULL,NULL),(3167,'',10,1,NULL,NULL),(3168,'',10,1,NULL,NULL),(3169,'',10,1,NULL,NULL),(3170,'',10,1,NULL,NULL),(3171,'',10,1,NULL,NULL),(3172,'',10,1,NULL,NULL),(3173,'',10,1,NULL,NULL),(3174,'',10,1,NULL,NULL),(3175,'',10,1,NULL,NULL),(3176,'',10,1,NULL,NULL),(3177,'',10,1,NULL,NULL),(3178,'',10,1,NULL,NULL),(3179,'',10,1,NULL,NULL),(3180,'',10,1,NULL,NULL),(3181,'',10,1,NULL,NULL),(3182,'',10,1,NULL,NULL),(3183,'',10,1,NULL,NULL),(3184,'',10,1,NULL,NULL),(3185,'',10,1,NULL,NULL),(3186,'',10,1,NULL,NULL),(3187,'',10,1,NULL,NULL),(3188,'',10,1,NULL,NULL),(3189,'',10,1,NULL,NULL),(3190,'',10,1,NULL,NULL),(3191,'',10,1,NULL,NULL),(3192,'',10,1,NULL,NULL),(3193,'',10,1,NULL,NULL),(3194,'',10,1,NULL,NULL),(3195,'',10,1,NULL,NULL),(3196,'',10,1,NULL,NULL),(3197,'',10,1,NULL,NULL),(3198,'',10,1,NULL,NULL),(3199,'',10,1,NULL,NULL),(3200,'',10,1,NULL,NULL),(3201,'',10,1,NULL,NULL),(3202,'',10,1,NULL,NULL),(3203,'',10,1,NULL,NULL),(3204,'',10,1,NULL,NULL),(3205,'',10,1,NULL,NULL),(3206,'',10,1,NULL,NULL),(3207,'',10,1,NULL,NULL),(3208,'',10,1,NULL,NULL),(3209,'',10,1,NULL,NULL),(3210,'',10,1,NULL,NULL),(3211,'',10,1,NULL,NULL),(3212,'',10,1,NULL,NULL),(3213,'',10,1,NULL,NULL),(3214,'',10,1,NULL,NULL),(3215,'',10,1,NULL,NULL),(3216,'',10,1,NULL,NULL),(3217,'',10,1,NULL,NULL),(3218,'',10,1,NULL,NULL),(3219,'',10,1,NULL,NULL),(3220,'',10,1,NULL,NULL),(3221,'',10,1,NULL,NULL),(3222,'',10,1,NULL,NULL),(3223,'',10,1,NULL,NULL),(3224,'',10,1,NULL,NULL),(3225,'',10,1,NULL,NULL),(3226,'',10,1,NULL,NULL),(3227,'',10,1,NULL,NULL),(3228,'',10,1,NULL,NULL),(3229,'',10,1,NULL,NULL),(3230,'',10,1,NULL,NULL),(3231,'',10,1,NULL,NULL),(3232,'',10,1,NULL,NULL),(3233,'',10,1,NULL,NULL),(3234,'',10,1,NULL,NULL),(3235,'',10,1,NULL,NULL),(3236,'',10,1,NULL,NULL),(3237,'',10,1,NULL,NULL),(3238,'',10,1,NULL,NULL),(3239,'',10,1,NULL,NULL),(3240,'',10,1,NULL,NULL),(3241,'',10,1,NULL,NULL),(3242,'',10,1,NULL,NULL),(3243,'',10,1,NULL,NULL),(3244,'',10,1,NULL,NULL),(3245,'',10,1,NULL,NULL),(3246,'',10,1,NULL,NULL),(3247,'',10,1,NULL,NULL),(3248,'',10,1,NULL,NULL),(3249,'',10,1,NULL,NULL),(3250,'',10,1,NULL,NULL),(3251,'',10,1,NULL,NULL),(3252,'',10,1,NULL,NULL),(3253,'',10,1,NULL,NULL),(3254,'',10,1,NULL,NULL),(3255,'',10,1,NULL,NULL),(3256,'',10,1,NULL,NULL),(3257,'',10,1,NULL,NULL),(3258,'',10,1,NULL,NULL),(3259,'',10,1,NULL,NULL),(3260,'',10,1,NULL,NULL),(3261,'',10,1,NULL,NULL),(3262,'',10,1,NULL,NULL),(3263,'',10,1,NULL,NULL),(3264,'',10,1,NULL,NULL),(3265,'',10,1,NULL,NULL),(3266,'',10,1,NULL,NULL),(3267,'',10,1,NULL,NULL),(3268,'',10,1,NULL,NULL),(3269,'',10,1,NULL,NULL),(3270,'',10,1,NULL,NULL),(3271,'',10,1,NULL,NULL),(3272,'',10,1,NULL,NULL),(3273,'',10,1,NULL,NULL),(3274,'',10,1,NULL,NULL),(3275,'',10,1,NULL,NULL),(3276,'',10,1,NULL,NULL),(3277,'',10,1,NULL,NULL),(3278,'',10,1,NULL,NULL),(3279,'',10,1,NULL,NULL),(3280,'',10,1,NULL,NULL),(3281,'',10,1,NULL,NULL),(3282,'',10,1,NULL,NULL),(3283,'',10,1,NULL,NULL),(3284,'',10,1,NULL,NULL),(3285,'',10,1,NULL,NULL),(3286,'',10,1,NULL,NULL),(3287,'',10,1,NULL,NULL),(3288,'',10,1,NULL,NULL),(3289,'',10,1,NULL,NULL),(3290,'',10,1,NULL,NULL),(3291,'',10,1,NULL,NULL),(3292,'',10,1,NULL,NULL),(3293,'',10,1,NULL,NULL),(3294,'',10,1,NULL,NULL),(3295,'',10,1,NULL,NULL),(3296,'',10,1,NULL,NULL),(3297,'',10,1,NULL,NULL),(3298,'',10,1,NULL,NULL),(3299,'',10,1,NULL,NULL),(3300,'',10,1,NULL,NULL),(3301,'',10,1,NULL,NULL),(3302,'',10,1,NULL,NULL),(3303,'',10,1,NULL,NULL),(3304,'',10,1,NULL,NULL),(3305,'',10,1,NULL,NULL),(3306,'',10,1,NULL,NULL),(3307,'',10,1,NULL,NULL),(3308,'',10,1,NULL,NULL),(3309,'',10,1,NULL,NULL),(3310,'',10,1,NULL,NULL),(3311,'',10,1,NULL,NULL),(3312,'',10,1,NULL,NULL),(3313,'',10,1,NULL,NULL),(3314,'',10,1,NULL,NULL),(3315,'',10,1,NULL,NULL),(3316,'',10,1,NULL,NULL),(3317,'',10,1,NULL,NULL),(3318,'',10,1,NULL,NULL),(3319,'',10,1,NULL,NULL),(3320,'',10,1,NULL,NULL),(3321,'',10,1,NULL,NULL),(3322,'',10,1,NULL,NULL),(3323,'',10,1,NULL,NULL),(3324,'',10,1,NULL,NULL),(3325,'',10,1,NULL,NULL),(3326,'',10,1,NULL,NULL),(3327,'',10,1,NULL,NULL),(3328,'',10,1,NULL,NULL),(3329,'',10,1,NULL,NULL),(3330,'',10,1,NULL,NULL),(3331,'',10,1,NULL,NULL),(3332,'',10,1,NULL,NULL),(3333,'',10,1,NULL,NULL),(3334,'',10,1,NULL,NULL),(3335,'',10,1,NULL,NULL),(3336,'',10,1,NULL,NULL),(3337,'',10,1,NULL,NULL),(3338,'',10,1,NULL,NULL),(3339,'',10,1,NULL,NULL),(3340,'',10,1,NULL,NULL),(3341,'',10,1,NULL,NULL),(3342,'',10,1,NULL,NULL),(3343,'',10,1,NULL,NULL),(3344,'',10,1,NULL,NULL),(3345,'',10,1,NULL,NULL),(3346,'',10,1,NULL,NULL),(3347,'',10,1,NULL,NULL),(3348,'',10,1,NULL,NULL),(3349,'',10,1,NULL,NULL),(3350,'',10,1,NULL,NULL),(3351,'',10,1,NULL,NULL),(3352,'',10,1,NULL,NULL),(3353,'',10,1,NULL,NULL),(3354,'',10,1,NULL,NULL),(3355,'',10,1,NULL,NULL),(3356,'',10,1,NULL,NULL),(3357,'',10,1,NULL,NULL),(3358,'',10,1,NULL,NULL),(3359,'',10,1,NULL,NULL),(3360,'',10,1,NULL,NULL),(3361,'',10,1,NULL,NULL),(3362,'',10,1,NULL,NULL),(3363,'',10,1,NULL,NULL),(3364,'',10,1,NULL,NULL),(3365,'',10,1,NULL,NULL),(3366,'',10,1,NULL,NULL),(3367,'',10,1,NULL,NULL),(3368,'',10,1,NULL,NULL),(3369,'',10,1,NULL,NULL),(3370,'',10,1,NULL,NULL),(3371,'',10,1,NULL,NULL),(3372,'',10,1,NULL,NULL),(3373,'',10,1,NULL,NULL),(3374,'',10,1,NULL,NULL),(3375,'',10,1,NULL,NULL),(3376,'',10,1,NULL,NULL),(3377,'',10,1,NULL,NULL),(3378,'',10,1,NULL,NULL),(3379,'',10,1,NULL,NULL),(3380,'',10,1,NULL,NULL),(3381,'',10,1,NULL,NULL),(3382,'',10,1,NULL,NULL),(3383,'',10,1,NULL,NULL),(3384,'',10,1,NULL,NULL),(3385,'',10,1,NULL,NULL),(3386,'',10,1,NULL,NULL),(3387,'',10,1,NULL,NULL),(3388,'',10,1,NULL,NULL),(3389,'',10,1,NULL,NULL),(3390,'',10,1,NULL,NULL),(3391,'',10,1,NULL,NULL),(3392,'',10,1,NULL,NULL),(3393,'',10,1,NULL,NULL),(3394,'',10,1,NULL,NULL),(3395,'',10,1,NULL,NULL),(3396,'',10,1,NULL,NULL),(3397,'',10,1,NULL,NULL),(3398,'',10,1,NULL,NULL),(3399,'',10,1,NULL,NULL),(3400,'',10,1,NULL,NULL),(3401,'',10,1,NULL,NULL),(3402,'',10,1,NULL,NULL),(3403,'',10,1,NULL,NULL),(3404,'',10,1,NULL,NULL),(3405,'',10,1,NULL,NULL),(3406,'',10,1,NULL,NULL),(3407,'',10,1,NULL,NULL),(3408,'',10,1,NULL,NULL),(3409,'',10,1,NULL,NULL),(3410,'',10,1,NULL,NULL),(3411,'',10,1,NULL,NULL),(3412,'',10,1,NULL,NULL),(3413,'',10,1,NULL,NULL),(3414,'',10,1,NULL,NULL),(3415,'',10,1,NULL,NULL),(3416,'',10,1,NULL,NULL),(3417,'',10,1,NULL,NULL),(3418,'',10,1,NULL,NULL),(3419,'',10,1,NULL,NULL),(3420,'',10,1,NULL,NULL),(3421,'',10,1,NULL,NULL),(3422,'',10,1,NULL,NULL),(3423,'',10,1,NULL,NULL),(3424,'',10,1,NULL,NULL),(3425,'',10,1,NULL,NULL),(3426,'',10,1,NULL,NULL),(3427,'',10,1,NULL,NULL),(3428,'',10,1,NULL,NULL),(3429,'',10,1,NULL,NULL),(3430,'',10,1,NULL,NULL),(3431,'',10,1,NULL,NULL),(3432,'',10,1,NULL,NULL),(3433,'',10,1,NULL,NULL),(3434,'',10,1,NULL,NULL),(3435,'',10,1,NULL,NULL),(3436,'',10,1,NULL,NULL),(3437,'',10,1,NULL,NULL),(3438,'',10,1,NULL,NULL),(3439,'',10,1,NULL,NULL),(3440,'',10,1,NULL,NULL),(3441,'',10,1,NULL,NULL),(3442,'',10,1,NULL,NULL),(3443,'',10,1,NULL,NULL),(3444,'',10,1,NULL,NULL),(3445,'',10,1,NULL,NULL),(3446,'',10,1,NULL,NULL),(3447,'',10,1,NULL,NULL),(3448,'',10,1,NULL,NULL),(3449,'',10,1,NULL,NULL),(3450,'',10,1,NULL,NULL),(3451,'',10,1,NULL,NULL),(3452,'',10,1,NULL,NULL),(3453,'',10,1,NULL,NULL),(3454,'',10,1,NULL,NULL),(3455,'',10,1,NULL,NULL),(3456,'',10,1,NULL,NULL),(3457,'',10,1,NULL,NULL),(3458,'',10,1,NULL,NULL),(3459,'',10,1,NULL,NULL),(3460,'',10,1,NULL,NULL),(3461,'',10,1,NULL,NULL),(3462,'',10,1,NULL,NULL),(3463,'',10,1,NULL,NULL),(3464,'',10,1,NULL,NULL),(3465,'',10,1,NULL,NULL),(3466,'',10,1,NULL,NULL),(3467,'',10,1,NULL,NULL),(3468,'',10,1,NULL,NULL),(3469,'',10,1,NULL,NULL),(3470,'',10,1,NULL,NULL),(3471,'',10,1,NULL,NULL),(3472,'',10,1,NULL,NULL),(3473,'',10,1,NULL,NULL),(3474,'',10,1,NULL,NULL),(3475,'',10,1,NULL,NULL),(3476,'',10,1,NULL,NULL),(3477,'',10,1,NULL,NULL),(3478,'',10,1,NULL,NULL),(3479,'',10,1,NULL,NULL),(3480,'',10,1,NULL,NULL),(3481,'',10,1,NULL,NULL),(3482,'',10,1,NULL,NULL),(3483,'',10,1,NULL,NULL),(3484,'',10,1,NULL,NULL),(3485,'',10,1,NULL,NULL),(3486,'',10,1,NULL,NULL),(3487,'',10,1,NULL,NULL),(3488,'',10,1,NULL,NULL),(3489,'',10,1,NULL,NULL),(3490,'',10,1,NULL,NULL),(3491,'',10,1,NULL,NULL),(3492,'',10,1,NULL,NULL),(3493,'',10,1,NULL,NULL),(3494,'',10,1,NULL,NULL),(3495,'',10,1,NULL,NULL),(3496,'',10,1,NULL,NULL),(3497,'',10,1,NULL,NULL),(3498,'',10,1,NULL,NULL),(3499,'',10,1,NULL,NULL),(3500,'',10,1,NULL,NULL),(3501,'',10,1,NULL,NULL),(3502,'',10,1,NULL,NULL),(3503,'',10,3,NULL,NULL),(3504,'',10,3,NULL,NULL),(3505,'',10,3,NULL,NULL),(3506,'',10,3,NULL,NULL),(3507,'',10,4,NULL,NULL),(3508,'',10,4,NULL,NULL),(3509,'',10,4,NULL,NULL),(3510,'',10,4,NULL,NULL),(3511,'',10,4,NULL,NULL),(3512,'',10,4,NULL,NULL),(3513,'',10,4,NULL,NULL),(3514,'',10,4,NULL,NULL),(3515,'',10,4,NULL,NULL),(3516,'',10,4,NULL,NULL),(3517,'',10,4,NULL,NULL),(3518,'',10,4,NULL,NULL),(3519,'',10,4,NULL,NULL),(3520,'',10,4,NULL,NULL),(3521,'',10,4,NULL,NULL),(3522,'',10,4,NULL,NULL),(3523,'',10,4,NULL,NULL),(3524,'',10,4,NULL,NULL),(3525,'',10,4,NULL,NULL),(3526,'',10,4,NULL,NULL),(3527,'',10,4,NULL,NULL),(3528,'',10,4,NULL,NULL),(3529,'',10,4,NULL,NULL),(3530,'',10,4,NULL,NULL),(3531,'',10,4,NULL,NULL),(3532,'',10,4,NULL,NULL),(3533,'',10,4,NULL,NULL),(3534,'',10,4,NULL,NULL),(3535,'',10,4,NULL,NULL),(3536,'',10,4,NULL,NULL),(3537,'',11,5,221,'2016-04-11 13:47:46'),(3538,'',11,5,NULL,NULL),(3539,'',11,5,NULL,NULL),(3540,'',11,5,NULL,NULL),(3541,'',11,5,NULL,NULL),(3542,'',11,5,NULL,NULL),(3543,'',11,5,NULL,NULL),(3544,'',11,5,NULL,NULL),(3545,'',11,5,NULL,NULL),(3546,'',11,5,NULL,NULL),(3547,'',11,5,NULL,NULL),(3548,'',11,5,NULL,NULL),(3549,'',11,5,NULL,NULL),(3550,'',11,5,NULL,NULL),(3551,'',11,5,NULL,NULL),(3552,'',11,5,NULL,NULL),(3553,'',11,5,NULL,NULL),(3554,'',11,5,NULL,NULL),(3555,'',11,5,NULL,NULL),(3556,'',11,5,NULL,NULL),(3557,'',11,5,NULL,NULL),(3558,'',11,5,NULL,NULL),(3559,'',11,5,NULL,NULL),(3560,'',11,5,NULL,NULL),(3561,'',11,5,NULL,NULL),(3562,'',11,5,NULL,NULL),(3563,'',11,5,NULL,NULL),(3564,'',11,5,NULL,NULL),(3565,'',11,5,NULL,NULL),(3566,'',11,5,NULL,NULL);
/*!40000 ALTER TABLE `license_licensegrant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mcka_apros_test_sessiontest`
--

DROP TABLE IF EXISTS `mcka_apros_test_sessiontest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mcka_apros_test_sessiontest` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `csfrtoken` varchar(20) NOT NULL,
  `token` varchar(20) NOT NULL,
  `expires` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mcka_apros_test_sessiontest`
--

LOCK TABLES `mcka_apros_test_sessiontest` WRITE;
/*!40000 ALTER TABLE `mcka_apros_test_sessiontest` DISABLE KEYS */;
/*!40000 ALTER TABLE `mcka_apros_test_sessiontest` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mcka_apros_test_usertest`
--

DROP TABLE IF EXISTS `mcka_apros_test_usertest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mcka_apros_test_usertest` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `first_name` varchar(20) NOT NULL,
  `last_name` varchar(20) NOT NULL,
  `email` varchar(20) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_mcka_admin` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mcka_apros_test_usertest`
--

LOCK TABLES `mcka_apros_test_usertest` WRITE;
/*!40000 ALTER TABLE `mcka_apros_test_usertest` DISABLE KEYS */;
/*!40000 ALTER TABLE `mcka_apros_test_usertest` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `public_api_apitoken`
--

DROP TABLE IF EXISTS `public_api_apitoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `public_api_apitoken` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `token` varchar(200) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `client_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  UNIQUE KEY `client_id` (`client_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `public_api_apitoken`
--

LOCK TABLES `public_api_apitoken` WRITE;
/*!40000 ALTER TABLE `public_api_apitoken` DISABLE KEYS */;
/*!40000 ALTER TABLE `public_api_apitoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `south_migrationhistory`
--

DROP TABLE IF EXISTS `south_migrationhistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `south_migrationhistory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_name` varchar(255) NOT NULL,
  `migration` varchar(255) NOT NULL,
  `applied` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `south_migrationhistory`
--

LOCK TABLES `south_migrationhistory` WRITE;
/*!40000 ALTER TABLE `south_migrationhistory` DISABLE KEYS */;
INSERT INTO `south_migrationhistory` VALUES (1,'admin','0001_initial','2016-03-16 09:20:11'),(2,'admin','0002_add_model_ClientNavLinks','2016-03-16 09:20:12'),(3,'admin','0003_auto__add_unique_clientnavlinks_client_id_link_name','2016-03-16 09:20:12'),(4,'admin','0004_add_model_ClientCustomization','2016-03-16 09:20:12'),(5,'admin','0005_auto__add_field_clientcustomization_hex_page_background','2016-03-16 09:20:12'),(6,'admin','0006_auto__add_field_clientcustomization_client_logo','2016-03-16 09:20:12'),(7,'admin','0007_auto__add_field_clientcustomization_hex_notification_text','2016-03-16 09:20:12'),(8,'admin','0008_add_model_AccessKey','2016-03-16 09:20:12'),(9,'admin','0009_auto__add_field_clientcustomization_identity_provider__del_field_acces','2016-03-16 09:20:12'),(10,'admin','0010_auto__add_field_clientcustomization_client_background__add_field_clien','2016-03-16 09:20:12'),(11,'admin','0011_auto__add_dashboardadminquickfilter','2016-03-16 09:20:12'),(12,'accounts','0001_initial','2016-03-16 09:20:13'),(13,'accounts','0002_user_activation','2016-03-16 09:20:13'),(14,'accounts','0003_user_activation','2016-03-16 09:20:13'),(15,'accounts','0004_user_activation','2016-03-16 09:20:13'),(16,'main','0001_initial','2016-03-16 09:20:13'),(17,'main','0002_auto__add_field_curatedcontentitem_sequence','2016-03-16 09:20:13'),(18,'main','0003_auto__add_field_curatedcontentitem_twitter_username','2016-03-16 09:20:13'),(19,'main','0004_auto__add_field_curatedcontentitem_thumbnail_url','2016-03-16 09:20:13'),(20,'main','0005_auto__add_field_curatedcontentitem_source__add_field_curatedcontentite','2016-03-16 09:20:13'),(21,'main','0006_auto__add_field_curatedcontentitem_created_at__add_field_curatedconten','2016-03-16 09:20:13'),(22,'main','0007_auto__add_field_curatedcontentitem_course_id','2016-03-16 09:20:13'),(23,'courses','0001_initial','2016-03-16 09:20:13'),(24,'courses','0002_auto__add_field_lessonnotesitem_user_id','2016-03-16 09:20:13'),(25,'courses','0003_auto__add_field_lessonnotesitem_module_id','2016-03-16 09:20:14'),(26,'courses','0004_auto__add_featureflags','2016-03-16 09:20:14'),(27,'courses','0005_auto__add_field_featureflags_proficiency','2016-03-16 09:20:14'),(28,'license','0001_initial','2016-03-16 09:20:14'),(29,'public_api','0001_initial','2016-03-16 09:20:14'),(30,'public_api','0002_auto__add_apitoken','2016-03-16 09:20:14'),(31,'public_api','0003_auto__add_field_apitoken_client_id','2016-03-16 09:20:14'),(32,'courses','0006_auto__add_field_featureflags_learner_dashboard','2016-03-17 09:39:53'),(35,'admin','0012_auto__add_learnersdashboard__add_batchoperationstatus__add_batchoperat','2016-03-30 13:11:55'),(36,'admin','0013_auto__chg_field_learnersdashboard_course_id__del_unique_learnersdashbo','2016-03-30 13:11:55'),(37,'admin','0014_auto__del_learnersdashboard__del_learnersdashboardtile__del_learnersda','2016-03-30 13:11:55'),(38,'admin','0015_auto__add_field_learnerdashboarddiscovery_order','2016-03-30 13:11:55'),(39,'admin','0016_auto__del_field_learnerdashboardtile_order__add_field_learnerdashboard','2016-03-30 13:11:56'),(40,'admin','0017_auto__chg_field_learnerdashboardresource_link__chg_field_learnerdashbo','2016-04-20 07:21:42'),(41,'accounts','0005_auto__add_field_useractivation_task_key__add_field_useractivation_firs','2016-04-20 07:21:42'),(42,'admin','0018_auto__add_emailtemplate','2016-04-26 08:56:08'),(43,'admin','0019_auto__del_field_learnerdashboardtile_description__del_field_learnerdas','2016-04-26 10:08:20'),(44,'admin','0020_auto__chg_field_emailtemplate_title','2016-04-28 08:57:04'),(45,'admin','0021_auto__del_field_brandingsettings_background_tiled__add_field_brandings','2016-04-28 10:49:19'),(46,'courses','0007_auto__add_field_featureflags_progress_page__add_field_featureflags_not','2016-04-28 10:49:19'),(47,'courses','0008_auto__add_field_featureflags_branding','2016-04-28 10:58:58'),(48,'admin','0022_auto__chg_field_learnerdashboarddiscovery_title','2016-04-28 12:16:01'),(49,'admin','0023_auto__chg_field_learnerdashboarddiscovery_author','2016-05-05 10:23:24'),(53,'admin','0024_auto__del_learnerdashboardresource__add_field_learnerdashboard_title_c','2016-05-10 07:58:06'),(54,'admin','0025_auto__add_companycontact__add_unique_companycontact_company_id_contact','2016-05-10 07:58:07'),(55,'admin','0026_auto__add_tilebookmark','2016-05-13 12:27:50');
/*!40000 ALTER TABLE `south_migrationhistory` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-08-24 10:16:03
