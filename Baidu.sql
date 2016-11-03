/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 50627
 Source Host           : localhost
 Source Database       : Baidu

 Target Server Type    : MySQL
 Target Server Version : 50627
 File Encoding         : utf-8

 Date: 11/03/2016 10:19:41 AM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `file_list`
-- ----------------------------
DROP TABLE IF EXISTS `file_list`;
CREATE TABLE `file_list` (
  `title` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `shorturl` varchar(100) DEFAULT NULL,
  `md5` varchar(100) DEFAULT NULL,
  `uk` bigint(100) DEFAULT NULL,
  `album` varchar(100) DEFAULT NULL,
  `type` int(11) DEFAULT NULL,
  `shareid` bigint(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- ----------------------------
--  Table structure for `share_list`
-- ----------------------------
DROP TABLE IF EXISTS `share_list`;
CREATE TABLE `share_list` (
  `intro` varchar(255) CHARACTER SET utf8 NOT NULL,
  `follow_count` int(11) NOT NULL,
  `fans_count` int(11) NOT NULL,
  `pubshare` int(11) NOT NULL,
  `uk` bigint(30) NOT NULL,
  `album_cout` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5680 DEFAULT CHARSET=latin1;

-- ----------------------------
--  Procedure structure for `1`
-- ----------------------------
DROP PROCEDURE IF EXISTS `1`;
delimiter ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `1`()
update share_list set pubshare = 0 where uk = 4077152221
 ;;
delimiter ;

SET FOREIGN_KEY_CHECKS = 1;
